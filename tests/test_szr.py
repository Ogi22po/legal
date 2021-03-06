# -*- coding: utf-8 -*-
#
# tests/test_szr.py
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
from datetime import datetime
from os.path import join

from bs4 import BeautifulSoup
from django.test import SimpleTestCase, TransactionTestCase, TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from legal.settings import TEST_DATA_DIR, FULL_CONTENT_TYPE
from legal.common.glob import LOCAL_DOMAIN
from legal.szr import cron, forms, models

from tests.utils import link_equal, check_html


APP = __package__.rpartition('.')[2]


class TestCron(TestCase):

    fixtures = ('szr_test.json',)

    def test_addauxid(self):

        cron.addauxid(models.Proceedings.objects.get(pk=1))

        proc = models.Proceedings.objects.get(pk=1)
        cron.addauxid(proc)
        self.assertEqual(proc.auxid, 0)

        proc = models.Proceedings.objects.get(pk=6)
        cron.addauxid(proc)
        self.assertEqual(proc.auxid, 173442)

        proc.auxid = 0
        proc.senate = 0
        cron.addauxid(proc)
        self.assertEqual(proc.auxid, 173443)

        proc.auxid = 0
        proc.year = 2014
        cron.addauxid(proc)
        self.assertEqual(proc.auxid, 0)

    def test_isreg(self):

        self.assertEqual(tuple(map(cron.isreg, models.Court.objects.order_by('pk'))), (True, False, False, False))

    def test_courts(self):

        models.Court.objects.all().delete()
        cron.cron_courts()
        court = models.Court.objects
        self.assertEqual(court.count(), 98)
        self.assertEqual(court.exclude(reports__isnull=True).count(), 86)

    def test_update(self):

        self.assertEqual(models.Proceedings.objects.filter(court_id='NSS', auxid=0).count(), 3)

        now = datetime.now()
        for dummy in range(models.Proceedings.objects.count()):
            cron.cron_update()
        self.assertEqual(models.Proceedings.objects.filter(court_id='NSS', auxid=0).count(), 1)

        ch6 = models.Proceedings.objects.get(pk=6).changed
        self.assertGreaterEqual(ch6, now)

        proc = models.Proceedings.objects.all().order_by('pk')
        self.assertEqual(
            tuple(proc.values_list('pk', 'changed', 'hash', 'notify')),
            (
                (1, datetime(2016, 10, 20, 12, 39, 6), 'a9684db1fe0cdb70703053137c9fa58e', True),
                (2, datetime(2016, 10, 2, 5, 56, 30), 'dd22b2b2bf9259973a75ca359337fec5', True),
                (3, datetime(2016, 11, 8, 4, 45, 31), '851e3d0e81bb44ba23ff6de85f106adf', True),
                (4, None, '6d1f956a99db7eb3ced0430e9dae8346', True),
                (5, None, 'b8096f084f58c5ae4bec1cf5effdaf6b', False),
                (6, ch6, '7091c453e984b1e4180442964e023b2e', True),
                (7, None, '33e51a9e60a51f4595a5bc5ed5f2a4aa', False),
            ))

    def test_szr_notice(self):

        self.assertEqual(cron.szr_notice(1), '')

        for dummy in range(models.Proceedings.objects.count()):
            cron.cron_update()

        self.assertEqual(
            cron.szr_notice(1),
            '''\
V těchto soudních řízeních, která sledujete, došlo ke změně:

 - Nejvyšší soud, sp. zn. 8 Tdo 819/2015
   http://infosoud.justice.cz/InfoSoud/public/search.do?org=NSJIMBM&krajOrg=NSJIMBM&cisloSenatu=8&druhVec=TDO&\
bcVec=819&rocnik=2015&typSoudu=ns&autoFill=true&type=spzn

 - Městský soud Praha, sp. zn. 41 T 3/2016 (Igor Ševcov)
   http://infosoud.justice.cz/InfoSoud/public/search.do?org=MSPHAAB&krajOrg=MSPHAAB&cisloSenatu=41&druhVec=T\
&bcVec=3&rocnik=2016&typSoudu=os&autoFill=true&type=spzn

 - Nejvyšší správní soud, sp. zn. 11 Kss 6/2015 (Miloš Zbránek)
   http://www.nssoud.cz/mainc.aspx?cls=InfoSoud&kau_id=173442

 - Městský soud Praha, sp. zn. 10 T 8/2014 (Opencard)
   http://infosoud.justice.cz/InfoSoud/public/search.do?org=MSPHAAB&krajOrg=MSPHAAB&cisloSenatu=10&druhVec=T\
&bcVec=8&rocnik=2014&typSoudu=os&autoFill=true&type=spzn

 - Obvodní soud Praha 2, sp. zn. 6 T 136/2013 (RWU)
   http://infosoud.justice.cz/InfoSoud/public/search.do?org=OSPHA02&krajOrg=MSPHAAB&cisloSenatu=6&druhVec=T\
&bcVec=136&rocnik=2013&typSoudu=os&autoFill=true&type=spzn

''')


class TestForms(TestCase):

    fixtures = ('szr_test.json',)

    def test_courtval(self):

        with self.assertRaises(ValidationError):
            forms.courtval('XXX')
        forms.courtval('NSS')


class TestModels(SimpleTestCase):

    def test_models(self):

        court = models.Court(
            id='NSJIMBM',
            name='Nejvyšší soud')

        self.assertEqual(str(court), 'Nejvyšší soud')

        self.assertEqual(
            str(models.Proceedings(
                uid_id=1,
                court=court,
                senate=7,
                register='Tdo',
                number=315,
                year=2000)),
            'Nejvyšší soud, 7 Tdo 315/2000')


class TestViews1(TransactionTestCase):

    fixtures = ('szr_test.json',)

    def setUp(self):
        User.objects.create_user('user', 'user@' + LOCAL_DOMAIN, 'none')
        self.user = User.objects.get(username='user')

    def tearDown(self):
        self.client.logout()

    def test_mainpage(self):

        res = self.client.get('/szr')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/szr/')
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

        res = self.client.get('/szr/', follow=True)
        self.assertTemplateUsed(res, 'login.xhtml')

        self.assertTrue(self.client.login(username='user', password='none'))

        res = self.client.get('/szr/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], FULL_CONTENT_TYPE)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/',
            {'email': 'xxx',
             'submit': 'Změnit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/',
            {'email': 'alt@' + LOCAL_DOMAIN,
             'submit': 'Změnit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.user = User.objects.get(username='user')
        self.assertEqual(self.user.email, 'alt@' + LOCAL_DOMAIN)
        check_html(self, res.content)

        res = self.client.get('/szr/')
        soup = BeautifulSoup(res.content, 'html.parser')
        self.assertFalse(soup.select('table#list'))
        check_html(self, res.content)

        self.client.force_login(User.objects.get(pk=1))

        res = self.client.get('/szr/')
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        self.assertEqual(len(soup.select('table#list tbody tr')), 7)
        models.Proceedings(
            uid_id=1,
            court_id='OSPHA02',
            senate=15,
            register='C',
            number=13287,
            year=2016,
            desc='Test').save()

        res = self.client.get('/szr/')
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        self.assertEqual(len(soup.select('table#list tbody tr')), 8)
        for number in range(200, 437):
            models.Proceedings(
                uid_id=1,
                court_id='OSPHA02',
                senate=15,
                register='C',
                number=number,
                year=2016,
                desc='Test {:d}'.format(number)).save()

        res = self.client.get('/szr/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertEqual(len(res.context['rows']), 50)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 4)
        self.assertEqual(links[0]['href'], '/szr/procform/')
        self.assertEqual(links[1]['href'], '#')
        self.assertTrue(link_equal(links[2]['href'], '/szr/?start=50'))
        self.assertTrue(link_equal(links[3]['href'], '/szr/?start=200'))

        res = self.client.get('/szr/?start=50')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertEqual(len(res.context['rows']), 50)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 6)
        self.assertEqual(links[0]['href'], '/szr/procform/')
        self.assertTrue(link_equal(links[1]['href'], '/szr/?start=0'))
        self.assertTrue(link_equal(links[2]['href'], '/szr/?start=0'))
        self.assertEqual(links[3]['href'], '#')
        self.assertTrue(link_equal(links[4]['href'], '/szr/?start=100'))
        self.assertTrue(link_equal(links[5]['href'], '/szr/?start=200'))

        res = self.client.get('/szr/?start=100')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertEqual(len(res.context['rows']), 50)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 6)
        self.assertEqual(links[0]['href'], '/szr/procform/')
        self.assertTrue(link_equal(links[1]['href'], '/szr/?start=0'))
        self.assertTrue(link_equal(links[2]['href'], '/szr/?start=50'))
        self.assertEqual(links[3]['href'], '#')
        self.assertTrue(link_equal(links[4]['href'], '/szr/?start=150'))
        self.assertTrue(link_equal(links[5]['href'], '/szr/?start=200'))

        res = self.client.get('/szr/?start=200')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertEqual(len(res.context['rows']), 45)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 4)
        self.assertEqual(links[0]['href'], '/szr/procform/')
        self.assertTrue(link_equal(links[1]['href'], '/szr/?start=0'))
        self.assertTrue(link_equal(links[2]['href'], '/szr/?start=150'))
        self.assertEqual(links[3]['href'], '#')

        res = self.client.get('/szr/?start=500')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertEqual(len(res.context['rows']), 1)
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.select('.list tfoot a')
        self.assertEqual(len(links), 4)
        self.assertEqual(links[0]['href'], '/szr/procform/')
        self.assertTrue(link_equal(links[1]['href'], '/szr/?start=0'))
        self.assertTrue(link_equal(links[2]['href'], '/szr/?start=194'))
        self.assertEqual(links[3]['href'], '#')


class TestViews2(TransactionTestCase):

    fixtures = ('szr_test.json',)

    def setUp(self):
        User.objects.create_user('user', 'user@' + LOCAL_DOMAIN, 'none')
        self.user = User.objects.get(username='user')

    def tearDown(self):
        self.client.logout()

    def test_procform(self):

        res = self.client.get('/szr/procform')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/szr/procform/')
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

        res = self.client.get('/szr/procform/', follow=True)
        self.assertTemplateUsed(res, 'login.xhtml')

        self.client.force_login(User.objects.get(pk=1))

        res = self.client.get('/szr/procform/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], FULL_CONTENT_TYPE)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        title = soup.select('h1')
        self.assertEqual(len(title), 1)
        self.assertEqual(title[0].text, 'Nové řízení')

        res = self.client.post(
            '/szr/procform/',
            {'register': 'C',
             'number': '110',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'XXX',
             'register': 'C',
             'number': '110',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '-1',
             'register': 'C',
             'number': '110',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': 'XXX',
             'register': 'C',
             'number': '110',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'number': '110',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'XXX',
             'number': '110',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': '0',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': 'XXX',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': '110',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': '110',
             'year': '1989',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': '110',
             'year': 'XXX',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        self.assertContains(res, 'Chybné zadání, prosím, opravte údaje')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'submit_back': 'Zpět bez uložení'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': '110',
             'year': '2016',
             'desc': 'Test 6',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': '110',
             'year': '2016',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/',
            {'court': 'MSPHAAB',
             'register': 'C',
             'number': '110',
             'year': '2016',
             'desc': 'Test',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        check_html(self, res.content)

        proc_id = models.Proceedings.objects.create(
            uid_id=1,
            court_id='MSPHAAB',
            senate=52,
            register='C',
            number=1,
            year=2016,
            desc='Test 2').id

        res = self.client.get('/szr/procform/{:d}/'.format(proc_id))
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], FULL_CONTENT_TYPE)
        self.assertTemplateUsed(res, 'szr_procform.xhtml')
        check_html(self, res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        title = soup.select('h1')
        self.assertEqual(len(title), 1)
        self.assertEqual(title[0].text, 'Úprava řízení')

        res = self.client.post(
            '/szr/procform/{:d}/'.format(proc_id),
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': '110',
             'year': '2016',
             'desc': 'Test 8',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        proc = models.Proceedings.objects.get(pk=proc_id)
        self.assertEqual(proc.senate, 52)
        self.assertEqual(proc.register, 'C')
        self.assertEqual(proc.number, 110)
        self.assertEqual(proc.year, 2016)
        self.assertEqual(proc.desc, 'Test 8')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procform/{:d}/'.format(proc_id),
            {'court': 'MSPHAAB',
             'senate': '52',
             'register': 'C',
             'number': '110',
             'year': '2016',
             'desc': 'Test 9',
             'submit': 'Uložit'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        proc = models.Proceedings.objects.get(pk=proc_id)
        self.assertEqual(proc.senate, 52)
        self.assertEqual(proc.register, 'C')
        self.assertEqual(proc.number, 110)
        self.assertEqual(proc.year, 2016)
        self.assertEqual(proc.desc, 'Test 9')
        check_html(self, res.content)


class TestViews3(TransactionTestCase):

    fixtures = ('szr_test.json',)

    def setUp(self):
        User.objects.create_user('user', 'user@' + LOCAL_DOMAIN, 'none')
        self.user = User.objects.get(username='user')

    def tearDown(self):
        self.client.logout()

    def test_procdel(self):

        proc_id = models.Proceedings.objects.create(
            uid=self.user,
            court_id='MSPHAAB',
            senate=52,
            register='C',
            number=1,
            year=2016,
            desc='Test').id

        res = self.client.get('/szr/procdel/{:d}'.format(proc_id))
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/szr/procdel/{:d}/'.format(proc_id))
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

        res = self.client.get('/szr/procdel/{:d}/'.format(proc_id), follow=True)
        self.assertTemplateUsed(res, 'login.xhtml')

        self.assertTrue(self.client.login(username='user', password='none'))

        res = self.client.get('/szr/procdel/{:d}/'.format(proc_id))
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procdel.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procdel/{:d}/'.format(proc_id),
            {'submit_no': 'Ne'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procdel/{:d}/'.format(proc_id),
            {'submit_yes': 'Ano'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procdeleted.xhtml')
        self.assertFalse(models.Proceedings.objects.filter(pk=proc_id).exists())
        check_html(self, res.content)

        res = self.client.post('/szr/procdel/{:d}/'.format(proc_id))
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)


class TestViews4(TransactionTestCase):

    fixtures = ('szr_test.json',)

    def setUp(self):
        User.objects.create_user('user', 'user@' + LOCAL_DOMAIN, 'none')
        self.user = User.objects.get(username='user')

    def tearDown(self):
        self.client.logout()

    def test_procdelall(self):

        models.Proceedings.objects.create(
            uid=self.user,
            court_id='MSPHAAB',
            senate=52,
            register='C',
            number=1,
            year=2016,
            desc='Test 1')

        models.Proceedings.objects.create(
            uid=self.user,
            court_id='MSPHAAB',
            senate=52,
            register='C',
            number=2,
            year=2016,
            desc='Test 2')

        self.assertEqual(models.Proceedings.objects.filter(uid=self.user).count(), 2)

        res = self.client.get('/szr/procdelall')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/szr/procdelall/')
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

        res = self.client.get('/szr/procdelall/', follow=True)
        self.assertTemplateUsed(res, 'login.xhtml')

        self.assertTrue(self.client.login(username='user', password='none'))

        res = self.client.get('/szr/procdelall/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procdelall.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procdelall/',
            {'submit_no': 'Ne'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procdelall/',
            {'submit_yes': 'Ano'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertEqual(models.Proceedings.objects.filter(uid=self.user).count(), 2)
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procdelall/',
            {'submit_yes': 'Ano',
             'conf': 'ano'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertEqual(models.Proceedings.objects.filter(uid=self.user).count(), 2)
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procdelall/',
            {'submit_yes': 'Ano',
             'conf': 'Ano'},
            follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_mainpage.xhtml')
        self.assertFalse(models.Proceedings.objects.filter(uid=self.user).exists())
        check_html(self, res.content)


class TestViews5(TransactionTestCase):

    fixtures = ('szr_test.json',)

    def setUp(self):
        User.objects.create_user('user', 'user@' + LOCAL_DOMAIN, 'none')
        self.user = User.objects.get(username='user')

    def tearDown(self):
        self.client.logout()

    def test_procbatchform(self):

        models.Proceedings.objects.create(
            uid=self.user,
            court_id='MSPHAAB',
            senate=52,
            register='C',
            number=1,
            year=2016,
            desc='Test 01')

        models.Proceedings.objects.create(
            uid=self.user,
            court_id='MSPHAAB',
            senate=52,
            register='C',
            number=4,
            year=2011,
            desc='Test 13')

        models.Proceedings.objects.create(
            uid=self.user,
            court_id='MSPHAAB',
            senate=52,
            register='C',
            number=5,
            year=2012,
            desc='Test 13')

        res = self.client.get('/szr/procbatchform')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/szr/procbatchform/')
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

        res = self.client.get('/szr/procbatchform/', follow=True)
        self.assertTemplateUsed(res, 'login.xhtml')

        self.assertTrue(self.client.login(username='user', password='none'))

        res = self.client.get('/szr/procbatchform/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procbatchform.xhtml')
        check_html(self, res.content)

        res = self.client.post(
            '/szr/procbatchform/',
            {'submit_load': 'Načíst'})
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procbatchform.xhtml')
        self.assertContains(res, 'Nejprve zvolte soubor k načtení')
        check_html(self, res.content)

        with open(join(TEST_DATA_DIR, 'szr_import.csv'), 'rb') as infile:
            res = self.client.post(
                '/szr/procbatchform/',
                {'submit_load': 'Načíst',
                 'load': infile},
                follow=True)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, 'szr_procbatchresult.xhtml')
        self.assertEqual(models.Proceedings.objects.count(), 13)
        self.assertEqual(res.context['count'], 4)
        self.assertEqual(
            res.context['errors'],
            [(3, 'Chybná zkratka soudu'),
             (4, 'Chybná zkratka soudu'),
             (5, 'Chybný formát'),
             (8, 'Chybná spisová značka'),
             (9, 'Chybná spisová značka'),
             (10, 'Chybná spisová značka'),
             (11, 'Chybná spisová značka'),
             (12, 'Chybná spisová značka'),
             (13, 'Popisu "Test 13" odpovídá více než jedno řízení'),
             (14, 'Prázdný popis'),
             (16, 'Příliš dlouhý popis')])
        check_html(self, res.content)

        res = self.client.get('/szr/procexport/')
        self.assertEqual(
            res.content.decode('utf-8'),
            '''\
Test 01,MSPHAAB,45 A 27/2014
Test 06,MSPHAAB,Nc 1070/2016
Test 07,MSPHAAB,Nc 1071/2016
Test 13,MSPHAAB,52 C 4/2011
Test 13,MSPHAAB,52 C 5/2012
{},MSPHAAB,45 A 27/2014
'''.format('T' * 255).replace('\n', '\r\n'))


class TestViews6(TransactionTestCase):

    fixtures = ('szr_test.json',)

    def setUp(self):
        User.objects.create_user('user', 'user@' + LOCAL_DOMAIN, 'none')
        self.user = User.objects.get(username='user')

    def tearDown(self):
        self.client.logout()

    def test_procexport(self):

        models.Proceedings.objects.create(
            uid=self.user,
            court_id='MSPHAAB',
            senate=52,
            register='C',
            number=1,
            year=2016,
            desc='Test 1')

        models.Proceedings.objects.create(
            uid=self.user,
            court_id='MSPHAAB',
            senate=0,
            register='Nc',
            number=512,
            year=2009,
            desc='Test 2')

        res = self.client.get('/szr/procexport')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/szr/procexport/')
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

        res = self.client.get('/szr/procexport/', follow=True)
        self.assertTemplateUsed(res, 'login.xhtml')

        self.assertTrue(self.client.login(username='user', password='none'))

        res = self.client.get('/szr/procexport/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], 'text/csv; charset=utf-8')
        self.assertEqual(
            res.content.decode('utf-8'),
            'Test 1,MSPHAAB,52 C 1/2016\r\nTest 2,MSPHAAB,Nc 512/2009\r\n')


class TestViews7(TransactionTestCase):

    fixtures = ('szr_test.json',)

    def setUp(self):
        User.objects.create_user('user', 'user@' + LOCAL_DOMAIN, 'none')
        self.user = User.objects.get(username='user')

    def tearDown(self):
        self.client.logout()

    def test_courts(self):

        res = self.client.get('/szr/courts')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/szr/courts/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], FULL_CONTENT_TYPE)
        self.assertTemplateUsed(res, 'szr_courts.xhtml')
        self.assertEqual(
            tuple(res.context['rows']),
            ({'id': 'MSPHAAB', 'name': 'Městský soud Praha'},
             {'id': 'NSJIMBM', 'name': 'Nejvyšší soud'},
             {'id': 'NSS', 'name': 'Nejvyšší správní soud'},
             {'id': 'OSPHA02', 'name': 'Obvodní soud Praha 2'},
            ))
        check_html(self, res.content)
