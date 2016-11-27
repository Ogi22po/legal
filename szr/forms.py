# -*- coding: utf-8 -*-
#
# szr/forms.py
#
# Copyright (C) 2011-16 Tomáš Pecina <tomas@pecina.cz>
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

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from common import forms, fields, widgets
from common.glob import register_regex
from szr.models import Court
from .glob import supreme_court

class EmailForm(forms.Form):
    email = fields.EmailField(
        widget=widgets.emw(),
        max_length=60,
        label='E-mail')

def courtval(c):
    if not Court.objects.filter(id=c).exists():
        raise ValidationError('Court does not exist')

class ProcForm(forms.Form):
    court = fields.CharField(
        widget=widgets.abbrw(),
        max_length=30,
        label='Soud',
        initial=supreme_court,
        validators=[courtval])
    senate = fields.IntegerField(
        widget=widgets.saw(),
        min_value=0,
        initial='',
        required=False)
    register = fields.CharField(
        widget=widgets.saw(),
        max_length=30,
        initial='',
        validators=[RegexValidator(regex=register_regex)])
    number = fields.IntegerField(
        widget=widgets.saw(),
        min_value=1,
        initial='')
    year = fields.IntegerField(
        widget=widgets.saw(),
        min_value=1990,
        initial='')
    desc = fields.CharField(
        widget=widgets.genw(),
        max_length=255,
        label='Popis',
        required=False)
