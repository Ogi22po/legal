# -*- coding: utf-8 -*-
#
# sop/forms.py
#
# Copyright (C) 2011-17 Tomáš Pecina <tomas@pecina.cz>
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

from datetime import date

from legal.common import forms, fields, widgets


OPTS = (
    ('none', 'sine'),
    ('epr', 'EPR'),
    ('nmu', 'nemajetková újma'),
    ('vyz', 'výživné'),
    ('vyk', 'výkon rozhodnutí'),
    ('sm', 'smír'),
    ('inc', 'incidence'),
    ('usch', 'úschova'),
)


class MainForm(forms.Form):

    basis = fields.AmountField(
        widget=widgets.MWidget(),
        min_value=1,
        label='Základ',
        localize=True)
    basis.rounding = 2

    curr = fields.CurrencyField(
        label='Měna',
        czk=True,
        initial='CZK')

    today = date.today()
    fx_date = fields.DateField(
        widget=widgets.DateWidget(),
        required=False,
        label='ke dni',
        initial=date(today.year, today.month, 1))

    model = fields.CharField(
        label='Úprava',
        initial='4')

    opt = fields.ChoiceField(
        widget=widgets.RadioWidget(),
        choices=OPTS,
        label='Zvláštní případy',
        initial='none')

    def clean_fx_date(self):
        data = self.cleaned_data['fx_date']
        if self.data['curr_0'] != 'CZK' and not data:
            raise forms.ValidationError('Date is required')
        return data
