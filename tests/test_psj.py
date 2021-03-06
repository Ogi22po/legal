# -*- coding: utf-8 -*-
#
# tests/test_psj.py
#
# Copyright (C) 2011-18 Tomáš Pecina <tomas@pecina.cz>
#
# This file is part of legal.pecina.cz, a web-based toolbox for lawyers.
#
# This application is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This application is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from http import HTTPStatus
from datetime import date, datetime
from locale import strxfrm
from os.path import join

from bs4 import BeautifulSoup
from django.apps import apps
from django.test import SimpleTestCase, TransactionTestCase, TestCase

from legal.settings import BASE_DIR, FULL_CONTENT_TYPE
from legal.szr.models import Court
from legal.psj import cron, forms, models, views

from tests.utils import strip_xml, validate_xml, link_equal, check_html

APP = __file__.rpartition('_')[2].partition('.')[0]
APPVERSION = apps.get_app_config(APP).version
with open(join(BASE_DIR, 'legal', APP, 'static', '{}-{}.xsd'.format(APP, APPVERSION)), 'rb') as xsdfile:
    XSD = xsdfile.read()


class TestCron(TestCase):

    fixtures = ('psj_test.json',)

    def test_courtrooms(self):

        cron.cron_courtrooms()
        self.assertEqual(models.Courtroom.objects.count(), 75)

        cron.cron_courtrooms()
        self.assertEqual(models.Courtroom.objects.count(), 75)

    def test_schedule(self):

        cron.cron_schedule('0')
        self.assertEqual(models.Task.objects.count(), 2)

        cron.cron_schedule('0', '1')
        self.assertEqual(models.Task.objects.count(), 4)

        cron.cron_schedule('1.1.2016')
        self.assertEqual(models.Task.objects.count(), 6)

    def test_update(self):

        cron.cron_courtrooms()
        models.Courtroom.objects.exclude(desc__contains='A003').delete()
        cron.cron_update()
        self.assertFalse(models.Hearing.objects.exists())

        cron.cron_schedule('1.12.2015')
        cron.cron_update()
        self.assertFalse(models.Hearing.objects.exists())

        models.Task.objects.all().delete()
        cron.cron_schedule('3.12.2016')
        cron.cron_update()
        self.assertFalse(models.Hearing.objects.exists())

        models.Task.objects.all().delete()
        cron.cron_schedule('1.12.2016')
        cron.cron_update()
        self.assertEqual(models.Hearing.objects.count(), 5)

        cron.cron_courtrooms()
        models.Courtroom.objects.exclude(desc__contains='101/').delete()
        cron.cron_update()
        self.assertEqual(models.Hearing.objects.count(), 2)


class TestForms(SimpleTestCase):

    def test_main_form(self):

        form = forms.MainForm(
            {'party_opt': 'icontains',
             'format': 'html'})
        self.assertTrue(form.is_valid())

        form = forms.MainForm(
            {'party_opt': 'icontains',
             'date_from': '2.3.2005',
             'date_to': '2.6.2001',
             'format': 'html'})
        self.assertFalse(form.is_valid())

        form = forms.MainForm(
            {'party_opt': 'icontains',
             'date_from': '2.3.2005',
             'date_to': '3.3.2005',
             'format': 'html'})
        self.assertTrue(form.is_valid())

        form = forms.MainForm(
            {'party_opt': 'icontains',
             'date_from': '2.3.2005',
             'date_to': '2.3.2005',
             'format': 'html'})
        self.assertTrue(form.is_valid())


class TestModels(TestCase):

    fixtures = ('psj_test.json',)

    def test_models(self):

        self.assertEqual(
            str(models.Courtroom(
                court_id='MSPHAAB',
                desc='test_courtroom')),
            'Městský soud Praha, test_courtroom')

        self.assertEqual(
            str(models.Party(
                name='test_party')),
            'test_party')

        self.assertEqual(
            str(models.Judge(
                name='test_judge')),
            'test_judge')

        cron.cron_courtrooms()
        self.assertEqual(
            str(models.Hearing(
                courtroom=models.Courtroom.objects.first(),
                time=datetime.now(),
                senate=4,
                register='C',
                number=26,
                year=2015,
                form_id=1,
                judge_id=1)),
            'Městský soud Praha, 4 C 26/2015')

        self.assertEqual(
            str(models.Task(
                court_id='MSPHAAB',
                date=date(2016, 1, 10))),
            'Městský soud Praha, 2016-01-10')


class TestViews1(SimpleTestCase):

    def test_stripjudge(self):

        cases = (
            ('Žlouťoučký Příliš', 'Žlouťoučký Příliš'),
            ('JUDr. Žlouťoučký Příliš', 'Žlouťoučký Příliš'),
            ('JUDr. Ing. Žlouťoučký Příliš', 'Žlouťoučký Příliš'),
        )

        for test in cases:
            self.assertTrue(
                test[0],
                views.stripjudge({'judge__name': test[0]}) == strxfrm(test[1]))


def populate():

    cron.cron_courtrooms()
    Court.objects.exclude(id='OSPHA02').delete()
    models.Courtroom.objects.exclude(desc__contains='101/').delete()
    cron.cron_schedule('1.12.2016')
    cron.cron_update()


class TestViews2(TransactionTestCase):

    fixtures = ('psj_test.json',)

    def test_mainpage(self):

        res = self.client.get('/psj')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/psj/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], FULL_CONTENT_TYPE)
        self.assertTemplateUsed(res, 'psj_mainpage.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/psj/',
            {'date_from': '1.1.2015',
             'date_to': '1.7.2016',
             'register': 'C',
             'party_opt': 'icontains',
             'format': 'html',
             'submit': 'Hledat'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/psj/',
            {'party': 'Ing',
             'party_opt': 'icontains',
             'format': 'html',
             'submit': 'Hledat'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.redirect_chain[0][1], HTTPStatus.FOUND)
        check_html(self, res.content)
        self.assertTrue(link_equal(res.redirect_chain[0][0], '/psj/list/?party=Ing&party_opt=icontains&start=0'))

        res = self.client.post(
            '/psj/',
            {'date_from': 'XXX',
             'party_opt': 'icontains',
             'format': 'html',
             'submit': 'Hledat'})
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_mainpage.xhtml')
        self.assertEqual(res.context['err_message'], 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/psj/',
            {'date_from': '1.1.2015',
             'date_to': '1.7.2014',
             'register': 'C',
             'party_opt': 'icontains',
             'format': 'html',
             'submit': 'Hledat'})
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_mainpage.xhtml')
        self.assertEqual(res.context['err_message'], 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)


class TestViews3(TransactionTestCase):

    fixtures = ('psj_test.json',)

    def setUp(self):
        populate()

    def test_htmllist(self):

        res = self.client.get('/psj/list')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.post('/psj/list/')
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        res = self.client.get('/psj/list/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], FULL_CONTENT_TYPE)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        check_html(self, res.content)

        res = self.client.get('/psj/list/?senate=-1')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?senate=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?register=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?register=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?number=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?number=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?year=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?year=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?courtroom=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?courtroom=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?judge=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?judge=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?date_from=2015-X-01')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?date_to=2015-X-01')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?party_opt=X')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?start=-1')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/list/?date_from=2015-01-01&date_to=2199-07-01&register=C&party_opt=icontains')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 2)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?start=100')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 2)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?register=T')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 0)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?date_from=2016-12-01')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 2)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?date_from=2016-12-02')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 0)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?date_to=2016-12-01')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 2)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?date_to=2016-11-30')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 0)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?court=OSPHA02')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 2)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?court=OSPHA03')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 0)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?courtroom={:d}'.format(models.Courtroom.objects.first().id))
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 2)

        res = self.client.get('/psj/list/?courtroom=9999')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 0)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?judge={:d}'.format(models.Hearing.objects.first().judge_id))
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 2)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?judge=9999')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 0)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?party=moroz&party_opt=icontains')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 1)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?party=mgr&party_opt=istartswith')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 1)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?party=zová&party_opt=iendswith')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 1)
        check_html(self, res.content)

        res = self.client.get('/psj/list/?party=mgr.+helena+morozová&party_opt=iexact')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(res.context['total'], 1)
        check_html(self, res.content)

        hear = models.Hearing.objects.first().__dict__
        del hear['id'], hear['_state']
        for number in range(200, 437):
            hear['number'] = number
            models.Hearing(**hear).save()

        res = self.client.get('/psj/list/?senate=26')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(len(res.context['rows']), 50)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 3)
        self.assertEqual(links[0]['href'], '#')
        self.assertTrue(link_equal(links[1]['href'], '/psj/list/?senate=26&start=50'))
        self.assertTrue(link_equal(links[2]['href'], '/psj/list/?senate=26&start=200'))

        res = self.client.get('/psj/list/?senate=26&start=50')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(len(res.context['rows']), 50)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 5)
        self.assertTrue(link_equal(links[0]['href'], '/psj/list/?senate=26&start=0'))
        self.assertTrue(link_equal(links[1]['href'], '/psj/list/?senate=26&start=0'))
        self.assertEqual(links[2]['href'], '#')
        self.assertTrue(link_equal(links[3]['href'], '/psj/list/?senate=26&start=100'))
        self.assertTrue(link_equal(links[4]['href'], '/psj/list/?senate=26&start=200'))

        res = self.client.get('/psj/list/?senate=26&start=100')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(len(res.context['rows']), 50)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 5)
        self.assertTrue(link_equal(links[0]['href'], '/psj/list/?senate=26&start=0'))
        self.assertTrue(link_equal(links[1]['href'], '/psj/list/?senate=26&start=50'))
        self.assertEqual(links[2]['href'], '#')
        self.assertTrue(link_equal(links[3]['href'], '/psj/list/?senate=26&start=150'))
        self.assertTrue(link_equal(links[4]['href'], '/psj/list/?senate=26&start=200'))

        res = self.client.get('/psj/list/?senate=26&start=200')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'psj_list.xhtml')
        self.assertEqual(len(res.context['rows']), 39)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 3)
        self.assertTrue(link_equal(links[0]['href'], '/psj/list/?senate=26&start=0'))
        self.assertTrue(link_equal(links[1]['href'], '/psj/list/?senate=26&start=150'))
        self.assertEqual(links[2]['href'], '#')


class TestViews4(TransactionTestCase):

    fixtures = ('psj_test.json',)

    def setUp(self):
        populate()

    def test_xmllist(self):

        res0 = '''<?xml version="1.0" encoding="utf-8"?>
<hearings application="psj" created="2016-11-18T15:43:27" version="1.1" xmlns="http://legal.pecina.cz" xmlns:xsi="ht\
tp://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://legal.pecina.cz https://legal.pecina.cz/static/p\
sj-1.1.xsd"><hearing><court id="OSPHA02">Obvodní soud Praha 2</court><courtroom>č. 101/přízemí - přístavba</courtroo\
m><time>2016-12-01T09:00:00</time><ref><senate>26</senate><register>C</register><number>181</number><year>2015</year\
></ref><judge>JUDr. Henzlová Šárka</judge><parties><party>ČR - Ministerstvo spravedlnosti ČR</party><party>Mgr. Hele\
na Morozová</party></parties><form>Jednání</form><closed>false</closed><cancelled>false</cancelled></hearing><hearin\
g><court id="OSPHA02">Obvodní soud Praha 2</court><courtroom>č. 101/přízemí - přístavba</courtroom><time>2016-12-01T\
12:00:00</time><ref><senate>26</senate><register>C</register><number>94</number><year>2015</year></ref><judge>JUDr. \
Henzlová Šárka</judge><parties><party>Česká republika - Ministerstvo spravedlnosti</party><party>Alois Hlásenský</pa\
rty></parties><form>Jednání</form><closed>false</closed><cancelled>false</cancelled></hearing></hearings>
'''

        res1 = '''<?xml version="1.0" encoding="utf-8"?>
<hearings application="psj" created="2016-11-18T16:00:01" version="1.1" xmlns="http://legal.pecina.cz" xmlns:xsi="ht\
tp://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://legal.pecina.cz https://legal.pecina.cz/static/p\
sj-1.1.xsd"><hearing><court id="OSPHA02">Obvodní soud Praha 2</court><courtroom>č. 101/přízemí - přístavba</courtroo\
m><time>2016-12-01T12:00:00</time><ref><senate>26</senate><register>C</register><number>94</number><year>2015</year>\
</ref><judge>JUDr. Henzlová Šárka</judge><parties><party>Česká republika - Ministerstvo spravedlnosti</party><party>\
Alois Hlásenský</party></parties><form>Jednání</form><closed>false</closed><cancelled>false</cancelled></hearing></h\
earings>
'''

        res = self.client.get('/psj/xmllist')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.post('/psj/xmllist/')
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        res = self.client.get('/psj/xmllist/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], 'text/xml; charset=utf-8')
        self.assertTrue(validate_xml(res.content, XSD))

        res = self.client.get('/psj/xmllist/?senate=-1')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?senate=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?register=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?register=XX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?number=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?number=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?year=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?year=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?courtroom=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?courtroom=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?judge=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?judge=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?date_from=2015-X-01')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?date_to=2015-X-01')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?party_opt=X')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/xmllist/?register=C')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertXMLEqual(strip_xml(res.content), strip_xml(res0.encode('utf-8')))
        self.assertTrue(validate_xml(res.content, XSD))

        res = self.client.get('/psj/xmllist/?party=oi&party_opt=icontains')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertXMLEqual(strip_xml(res.content), strip_xml(res1.encode('utf-8')))
        self.assertTrue(validate_xml(res.content, XSD))

        exlim = views.EXLIM
        views.EXLIM = 0
        res = self.client.get('/psj/xmllist/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'exlim.xhtml')
        check_html(self, res.content)
        views.EXLIM = exlim

    def test_csvlist(self):

        res0 = '''Soud,Jednací síň,Datum,Čas,Spisová značka,Řešitel,Účastníci řízení,Druh jednání,Neveřejné,Zrušeno
'''

        res1 = res0 + '''Obvodní soud Praha 2,č. 101/přízemí - přístavba,01.12.2016,09:00,26 C 181/2015,JUDr. Henzlo\
vá Šárka,ČR - Ministerstvo spravedlnosti ČR;Mgr. Helena Morozová,Jednání,ne,ne
Obvodní soud Praha 2,č. 101/přízemí - přístavba,01.12.2016,12:00,26 C 94/2015,JUDr. Henzlová Šárka,Česká republika -\
 Ministerstvo spravedlnosti;Alois Hlásenský,Jednání,ne,ne
'''

        res2 = res0 + '''Obvodní soud Praha 2,č. 101/přízemí - přístavba,01.12.2016,12:00,26 C 94/2015,JUDr. Henzlov\
á Šárka,Česká republika - Ministerstvo spravedlnosti;Alois Hlásenský,Jednání,ne,ne
'''

        res = self.client.get('/psj/csvlist')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.post('/psj/csvlist/')
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        res = self.client.get('/psj/csvlist/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], 'text/csv; charset=utf-8')

        res = self.client.get('/psj/csvlist/?senate=-1')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?senate=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?register=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?register=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?number=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?number=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?year=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?year=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?courtroom=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?courtroom=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?judge=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?judge=XXX')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?date_from=2015-X-01')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?date_to=2015-X-01')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?party_opt=X')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/csvlist/?register=T')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res.content.decode('utf-8').replace('\r\n', '\n'), res0)

        res = self.client.get('/psj/csvlist/?register=C')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res.content.decode('utf-8').replace('\r\n', '\n'), res1)

        res = self.client.get('/psj/csvlist/?party=oi&party_opt=icontains')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res.content.decode('utf-8').replace('\r\n', '\n'), res2)

        exlim = views.EXLIM
        views.EXLIM = 0
        res = self.client.get('/psj/csvlist/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'exlim.xhtml')
        check_html(self, res.content)
        views.EXLIM = exlim

    def test_jsonlist(self):

        res0 = '[]'

        res1 = '''[{"court": {"name": "Obvodn\u00ed soud Praha 2", "id": "OSPHA02"}, "judge": "JUDr. Henzlov\u00e1 \
\u0160\u00e1rka", "ref": {"senate": 26, "year": 2015, "number": 181, "register": "C"}, "form": "Jedn\u00e1n\u00ed", \
"courtroom": "\u010d. 101/p\u0159\u00edzem\u00ed - p\u0159\u00edstavba", "cancelled": false, "parties": ["\u010cR - \
Ministerstvo spravedlnosti \u010cR", "Mgr. Helena Morozov\u00e1"], "closed": false, "time": "2016-12-01T09:00:00"}, \
{"court": {"name": "Obvodn\u00ed soud Praha 2", "id": "OSPHA02"}, "judge": "JUDr. Henzlov\u00e1 \u0160\u00e1rka", "r\
ef": {"senate": 26, "year": 2015, "number": 94, "register": "C"}, "form": "Jedn\u00e1n\u00ed", "courtroom": "\u010d.\
 101/p\u0159\u00edzem\u00ed - p\u0159\u00edstavba", "cancelled": false, "parties": ["\u010cesk\u00e1 republika - Min\
isterstvo spravedlnosti", "Alois Hl\u00e1sensk\u00fd"], "closed": false, "time": "2016-12-01T12:00:00"}]'''

        res2 = '''[{"court": {"name": "Obvodn\u00ed soud Praha 2", "id": "OSPHA02"}, "cancelled": false, "judge": "J\
UDr. Henzlov\u00e1 \u0160\u00e1rka", "time": "2016-12-01T12:00:00", "courtroom": "\u010d. 101/p\u0159\u00edzem\u00ed\
 - p\u0159\u00edstavba", "closed": false, "form": "Jedn\u00e1n\u00ed", "parties": ["\u010cesk\u00e1 republika - Mini\
sterstvo spravedlnosti", "Alois Hl\u00e1sensk\u00fd"], "ref": {"year": 2015, "register": "C", "senate": 26, "number"\
: 94}}]'''

        res = self.client.get('/psj/jsonlist')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.post('/psj/jsonlist/')
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        res = self.client.get('/psj/jsonlist/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], 'application/json; charset=utf-8')

        res = self.client.get('/psj/jsonlist/?senate=-1')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?register=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?number=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?year=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?courtroom=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?judge=0')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?date_from=2015-X-01')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?date_to=2015-X-01')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?party_opt=X')
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

        res = self.client.get('/psj/jsonlist/?register=T')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertJSONEqual(res.content.decode('utf-8'), res0)

        res = self.client.get('/psj/jsonlist/?register=C')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertJSONEqual(res.content.decode('utf-8'), res1)

        res = self.client.get('/psj/jsonlist/?party=oi&party_opt=icontains')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertJSONEqual(res.content.decode('utf-8'), res2)

        exlim = views.EXLIM
        views.EXLIM = 0
        res = self.client.get('/psj/jsonlist/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'exlim.xhtml')
        check_html(self, res.content)
        views.EXLIM = exlim

    def test_courtinfo(self):

        res0 = '''<select id="courtroom"><option value="{:d}">č. 101/přízemí - přístavba</option></select><select id\
="judge"><option value="{:d}">JUDr. Henzlová Šárka</option></select>
'''

        res = self.client.get('/psj/court/OSPHA02')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.post('/psj/court/OSPHA02/')
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        res = self.client.get('/psj/court/OSPHA02/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], 'text/plain; charset=utf-8')
        self.assertTemplateUsed(res, 'psj_court.xhtml')
        croom = models.Courtroom.objects.get(desc__contains='101/').id
        judge = models.Judge.objects.get(name__contains='Hen').id
        self.assertHTMLEqual(res.content.decode('utf_8'), res0.format(croom, judge))
