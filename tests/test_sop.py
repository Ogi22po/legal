# -*- coding: utf-8 -*-
#
# tests/test_sop.py
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

from bs4 import BeautifulSoup
from django.test import SimpleTestCase, TestCase

from legal.settings import FULL_CONTENT_TYPE
from legal.sop import forms

from tests.utils import check_html


class TestForms(SimpleTestCase):

    def test_main_form(self):

        form = forms.MainForm(
            {'fx_date': '',
             'curr_0': 'EUR',
             'model': '1',
             'basis': '1000',
             'opt': 'none'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'fx_date': ['Date is required']})

        form = forms.MainForm(
            {'fx_date': '',
             'curr_0': 'CZK',
             'model': '1',
             'basis': '1000',
             'opt': 'none'})
        self.assertTrue(form.is_valid())

        form = forms.MainForm(
            {'fx_date': '6.6.2016',
             'curr_0': 'EUR',
             'model': '1',
             'basis': '1000',
             'opt': 'none'})
        self.assertTrue(form.is_valid())


class TestViews(TestCase):

    fixtures = ('sop_test.json',)

    def test_main(self):

        cases = (
            ('100000000', 'CZK', '', '', '1', 'none', '1.000.000'),
            ('1000000', 'CZK', '', '', '1', 'epr', '20.000'),
            ('100000000', 'CZK', '', '', '1', 'nmu', '1.000.000'),
            ('5000000', 'CZK', '', '', '1', 'vyz', '10.000'),
            ('10000000', 'CZK', '', '', '1', 'vyk', '50.000'),
            ('5000000', 'CZK', '', '', '1', 'sm', '20.000'),
            ('100000000', 'CZK', '', '', '1', 'inc', '1.000'),
            ('200000000', 'CZK', '', '', '1', 'usch', '1.000.000'),
            ('5690', 'EUR', '', '1.7.2016', '4', 'none', '4.864'),
            ('8000', 'USD', '', '1.7.2016', '4', 'none', '13.734'),
            ('29158900', 'OTH', 'THB', '1.7.2016', '4', 'none', '1.449.635'),
            ('1', 'CZK', '', '', '1', 'none', '600'),
            ('100', 'CZK', '', '', '1', 'none', '600'),
            ('1000', 'CZK', '', '', '1', 'none', '600'),
            ('15099,99', 'CZK', '', '', '1', 'none', '600'),
            ('15100,00', 'CZK', '', '', '1', 'none', '610'),
            ('25000000', 'CZK', '', '', '1', 'none', '1.000.000'),
            ('1', 'CZK', '', '', '1', 'epr', '300'),
            ('100', 'CZK', '', '', '1', 'epr', '300'),
            ('1000', 'CZK', '', '', '1', 'epr', '300'),
            ('15099,99', 'CZK', '', '', '1', 'epr', '300'),
            ('15100,00', 'CZK', '', '', '1', 'epr', '310'),
            ('1', 'CZK', '', '', '1', 'nmu', '600'),
            ('100', 'CZK', '', '', '1', 'nmu', '600'),
            ('1000', 'CZK', '', '', '1', 'nmu', '600'),
            ('15099,99', 'CZK', '', '', '1', 'nmu', '600'),
            ('15100,00', 'CZK', '', '', '1', 'nmu', '610'),
            ('25000000', 'CZK', '', '', '1', 'nmu', '1.000.000'),
            ('1', 'CZK', '', '', '1', 'vyz', '300'),
            ('30000', 'CZK', '', '', '1', 'vyz', '300'),
            ('1000000', 'CZK', '', '', '1', 'vyz', '10.000'),
            ('1', 'CZK', '', '', '1', 'vyk', '300'),
            ('15000', 'CZK', '', '', '1', 'vyk', '300'),
            ('2500000', 'CZK', '', '', '1', 'vyk', '50.000'),
            ('1', 'CZK', '', '', '1', 'sm', '300'),
            ('15000', 'CZK', '', '', '1', 'sm', '300'),
            ('1000000', 'CZK', '', '', '1', 'sm', '20.000'),
            ('1', 'CZK', '', '', '1', 'inc', '1.000'),
            ('1', 'CZK', '', '', '1', 'usch', '200'),
            ('20000', 'CZK', '', '', '1', 'usch', '200'),
            ('100000000', 'CZK', '', '', '1', 'usch', '1.000.000'),
            ('1', 'CZK', '', '', '2', 'none', '1.000'),
            ('100', 'CZK', '', '', '2', 'none', '1.000'),
            ('1000', 'CZK', '', '', '2', 'none', '1.000'),
            ('20099,99', 'CZK', '', '', '2', 'none', '1.000'),
            ('20100,00', 'CZK', '', '', '2', 'none', '1.010'),
            ('40000000', 'CZK', '', '', '2', 'none', '2.000.000'),
            ('40000100', 'CZK', '', '', '2', 'none', '2.000.010'),
            ('250000000', 'CZK', '', '', '2', 'none', '4.100.000'),
            ('1000000000', 'CZK', '', '', '2', 'none', '4.100.000'),
            ('1', 'CZK', '', '', '2', 'epr', '800'),
            ('100', 'CZK', '', '', '2', 'epr', '800'),
            ('1000', 'CZK', '', '', '2', 'epr', '800'),
            ('20099,99', 'CZK', '', '', '2', 'epr', '800'),
            ('20100,00', 'CZK', '', '', '2', 'epr', '810'),
            ('1000000', 'CZK', '', '', '2', 'epr', '40.000'),
            ('1', 'CZK', '', '', '2', 'nmu', '2.000'),
            ('100', 'CZK', '', '', '2', 'nmu', '2.000'),
            ('1000', 'CZK', '', '', '2', 'nmu', '2.000'),
            ('200099,99', 'CZK', '', '', '2', 'nmu', '2.000'),
            ('200100,00', 'CZK', '', '', '2', 'nmu', '2.010'),
            ('200000000', 'CZK', '', '', '2', 'nmu', '2.000.000'),
            ('1000000000', 'CZK', '', '', '2', 'nmu', '2.000.000'),
            ('1', 'CZK', '', '', '2', 'vyz', '500'),
            ('50000', 'CZK', '', '', '2', 'vyz', '500'),
            ('1500000', 'CZK', '', '', '2', 'vyz', '15.000'),
            ('5000000', 'CZK', '', '', '2', 'vyz', '15.000'),
            ('1', 'CZK', '', '', '2', 'vyk', '500'),
            ('25000', 'CZK', '', '', '2', 'vyk', '500'),
            ('3750000', 'CZK', '', '', '2', 'vyk', '75.000'),
            ('10000000', 'CZK', '', '', '2', 'vyk', '75.000'),
            ('1', 'CZK', '', '', '2', 'sm', '500'),
            ('25000', 'CZK', '', '', '2', 'sm', '500'),
            ('1500000', 'CZK', '', '', '2', 'sm', '30.000'),
            ('5000000', 'CZK', '', '', '2', 'sm', '30.000'),
            ('1', 'CZK', '', '', '2', 'inc', '1.000'),
            ('20000', 'CZK', '', '', '2', 'inc', '1.000'),
            ('100000000', 'CZK', '', '', '2', 'inc', '2.000.000'),
            ('500000000', 'CZK', '', '', '2', 'inc', '2.000.000'),
            ('1', 'CZK', '', '', '2', 'usch', '250'),
            ('25000', 'CZK', '', '', '2', 'usch', '250'),
            ('200000000', 'CZK', '', '', '2', 'usch', '2.000.000'),
            ('1000000000', 'CZK', '', '', '2', 'usch', '2.000.000'),
            ('1', 'CZK', '', '', '3', 'none', '1.000'),
            ('100', 'CZK', '', '', '3', 'none', '1.000'),
            ('1000', 'CZK', '', '', '3', 'none', '1.000'),
            ('20099,99', 'CZK', '', '', '3', 'none', '1.000'),
            ('20100,00', 'CZK', '', '', '3', 'none', '1.010'),
            ('40000000', 'CZK', '', '', '3', 'none', '2.000.000'),
            ('40000100', 'CZK', '', '', '3', 'none', '2.000.010'),
            ('250000000', 'CZK', '', '', '3', 'none', '4.100.000'),
            ('1000000000', 'CZK', '', '', '3', 'none', '4.100.000'),
            ('1', 'CZK', '', '', '3', 'epr', '400'),
            ('100', 'CZK', '', '', '3', 'epr', '400'),
            ('1000', 'CZK', '', '', '3', 'epr', '400'),
            ('10000', 'CZK', '', '', '3', 'epr', '400'),
            ('10099,99', 'CZK', '', '', '3', 'epr', '400'),
            ('10100,00', 'CZK', '', '', '3', 'epr', '800'),
            ('20099,99', 'CZK', '', '', '3', 'epr', '800'),
            ('20100,00', 'CZK', '', '', '3', 'epr', '810'),
            ('1000000', 'CZK', '', '', '3', 'epr', '40.000'),
            ('1', 'CZK', '', '', '3', 'nmu', '2.000'),
            ('100', 'CZK', '', '', '3', 'nmu', '2.000'),
            ('1000', 'CZK', '', '', '3', 'nmu', '2.000'),
            ('200099,99', 'CZK', '', '', '3', 'nmu', '2.000'),
            ('200100,00', 'CZK', '', '', '3', 'nmu', '2.010'),
            ('200000000', 'CZK', '', '', '3', 'nmu', '2.000.000'),
            ('1000000000', 'CZK', '', '', '3', 'nmu', '2.000.000'),
            ('1', 'CZK', '', '', '3', 'vyz', '500'),
            ('50000', 'CZK', '', '', '3', 'vyz', '500'),
            ('1500000', 'CZK', '', '', '3', 'vyz', '15.000'),
            ('5000000', 'CZK', '', '', '3', 'vyz', '15.000'),
            ('1', 'CZK', '', '', '3', 'vyk', '1.000'),
            ('20000', 'CZK', '', '', '3', 'vyk', '1.000'),
            ('40000000', 'CZK', '', '', '3', 'vyk', '2.000.000'),
            ('250000000', 'CZK', '', '', '3', 'vyk', '4.100.000'),
            ('1000000000', 'CZK', '', '', '3', 'vyk', '4.100.000'),
            ('1', 'CZK', '', '', '3', 'sm', '500'),
            ('25000', 'CZK', '', '', '3', 'sm', '500'),
            ('1500000', 'CZK', '', '', '3', 'sm', '30.000'),
            ('5000000', 'CZK', '', '', '3', 'sm', '30.000'),
            ('1', 'CZK', '', '', '3', 'inc', '1.000'),
            ('20000', 'CZK', '', '', '3', 'inc', '1.000'),
            ('100000000', 'CZK', '', '', '3', 'inc', '2.000.000'),
            ('500000000', 'CZK', '', '', '3', 'inc', '2.000.000'),
            ('1', 'CZK', '', '', '3', 'usch', '250'),
            ('25000', 'CZK', '', '', '3', 'usch', '250'),
            ('200000000', 'CZK', '', '', '3', 'usch', '2.000.000'),
            ('1000000000', 'CZK', '', '', '3', 'usch', '2.000.000'),
            ('1', 'CZK', '', '', '4', 'none', '1.000'),
            ('100', 'CZK', '', '', '4', 'none', '1.000'),
            ('1000', 'CZK', '', '', '4', 'none', '1.000'),
            ('20099,99', 'CZK', '', '', '4', 'none', '1.005'),
            ('20100,00', 'CZK', '', '', '4', 'none', '1.005'),
            ('1234567', 'CZK', '', '', '4', 'none', '61.728'),
            ('40000000', 'CZK', '', '', '4', 'none', '2.000.000'),
            ('40000100', 'CZK', '', '', '4', 'none', '2.000.001'),
            ('250000000', 'CZK', '', '', '4', 'none', '4.100.000'),
            ('1000000000', 'CZK', '', '', '4', 'none', '4.100.000'),
            ('1', 'CZK', '', '', '4', 'epr', '400'),
            ('100', 'CZK', '', '', '4', 'epr', '400'),
            ('1000', 'CZK', '', '', '4', 'epr', '400'),
            ('10000', 'CZK', '', '', '4', 'epr', '400'),
            ('10000,01', 'CZK', '', '', '4', 'epr', '800'),
            ('10099,99', 'CZK', '', '', '4', 'epr', '800'),
            ('10100,00', 'CZK', '', '', '4', 'epr', '800'),
            ('20099,99', 'CZK', '', '', '4', 'epr', '804'),
            ('20100,00', 'CZK', '', '', '4', 'epr', '804'),
            ('1000000', 'CZK', '', '', '4', 'epr', '40.000'),
            ('1', 'CZK', '', '', '4', 'nmu', '2.000'),
            ('100', 'CZK', '', '', '4', 'nmu', '2.000'),
            ('1000', 'CZK', '', '', '4', 'nmu', '2.000'),
            ('200099,99', 'CZK', '', '', '4', 'nmu', '2.001'),
            ('200100,00', 'CZK', '', '', '4', 'nmu', '2.001'),
            ('200000000', 'CZK', '', '', '4', 'nmu', '2.000.000'),
            ('1000000000', 'CZK', '', '', '4', 'nmu', '2.000.000'),
            ('1', 'CZK', '', '', '4', 'vyz', '500'),
            ('50000', 'CZK', '', '', '4', 'vyz', '500'),
            ('1500000', 'CZK', '', '', '4', 'vyz', '15.000'),
            ('5000000', 'CZK', '', '', '4', 'vyz', '15.000'),
            ('1', 'CZK', '', '', '4', 'vyk', '1.000'),
            ('20000', 'CZK', '', '', '4', 'vyk', '1.000'),
            ('40000000', 'CZK', '', '', '4', 'vyk', '2.000.000'),
            ('250000000', 'CZK', '', '', '4', 'vyk', '4.100.000'),
            ('1000000000', 'CZK', '', '', '4', 'vyk', '4.100.000'),
            ('1', 'CZK', '', '', '4', 'sm', '500'),
            ('25000', 'CZK', '', '', '4', 'sm', '500'),
            ('1500000', 'CZK', '', '', '4', 'sm', '30.000'),
            ('5000000', 'CZK', '', '', '4', 'sm', '30.000'),
            ('1', 'CZK', '', '', '4', 'inc', '1.000'),
            ('20000', 'CZK', '', '', '4', 'inc', '1.000'),
            ('100000000', 'CZK', '', '', '4', 'inc', '2.000.000'),
            ('500000000', 'CZK', '', '', '4', 'inc', '2.000.000'),
            ('1', 'CZK', '', '', '4', 'usch', '250'),
            ('25000', 'CZK', '', '', '4', 'usch', '250'),
            ('200000000', 'CZK', '', '', '4', 'usch', '2.000.000'),
            ('1000000000', 'CZK', '', '', '4', 'usch', '2.000.000'),
        )

        err_cases = (
            ('-100', 'CZK', '', '', '1', 'none'),
            ('0', 'CZK', '', '', '1', 'none'),
            ('0,01', 'CZK', '', '', '1', 'none'),
            ('0,99', 'CZK', '', '', '1', 'none'),
            ('1000000,01', 'CZK', '', '', '1', 'epr'),
            ('5690', 'EUR', '', '', '1', 'none'),
            ('5690', 'XXX', '', '1.7.2016', '1', 'none'),
        )

        res = self.client.get('/sop')
        self.assertEqual(res.status_code, HTTPStatus.MOVED_PERMANENTLY)

        res = self.client.get('/sop/')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(res.has_header('content-type'))
        self.assertEqual(res['content-type'], FULL_CONTENT_TYPE)
        self.assertTemplateUsed(res, 'sop_mainpage.xhtml')
        check_html(self, res.content)

        num = 1
        for test in cases:
            res = self.client.post(
                '/sop/',
                {'basis': test[0],
                 'curr_0': test[1],
                 'curr_1': test[2],
                 'fx_date': test[3],
                 'model': test[4],
                 'opt': test[5]})
            self.assertEqual(res.status_code, HTTPStatus.OK)
            self.assertTemplateUsed(res, 'sop_mainpage.xhtml')
            soup = BeautifulSoup(res.content, 'html.parser')
            msg = soup.find('td', 'msg').select('div')
            self.assertGreater(len(msg), 1)
            self.assertEqual(msg[1].text, '{} Kč'.format(test[6]))
            check = num < 12
            check_html(self, res.content, key=num, check_html=check, check_classes=check)
            num += 1

        num = 1
        for test in err_cases:
            res = self.client.post(
                '/sop/',
                {'basis': test[0],
                 'curr_0': test[1],
                 'curr_1': test[2],
                 'fx_date': test[3],
                 'model': test[4],
                 'opt': test[5]})
            self.assertEqual(res.status_code, HTTPStatus.OK)
            self.assertTemplateUsed(res, 'sop_mainpage.xhtml')
            soup = BeautifulSoup(res.content, 'html.parser')
            msg = soup.find('td', 'msg').select('div')
            self.assertEqual(len(msg), 1)
            check_html(self, res.content, key=num)
            num += 1
