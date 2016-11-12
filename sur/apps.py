# -*- coding: utf-8 -*-
#
# sur/apps.py
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

from django.apps import AppConfig
from datetime import datetime, timedelta

class SurConfig(AppConfig):
    name = 'sur'
    verbose_name = 'Sledování účastníků řízení'
    version = '1.0'

    def stat(self):
        from .models import Party, Found
        now = datetime.now()
        return [
            [
                'Počet účastníků řízení',
                Party.objects.count()],
            [
                'Počet nových účastníků řízení za posledních 24 hodin',
                Party.objects.filter(timestamp__gte=(now - \
                    timedelta(hours=24))).count()],
            [
                'Počet nových účastníků řízení za poslední týden',
                Party.objects.filter(timestamp__gte=(now - \
                    timedelta(weeks=1))).count()],
            [
                'Počet nových účastníků řízení za poslední měsíc',
                Party.objects.filter(timestamp__gte=(now - \
                    timedelta(days=30))).count()],
            [
                'Počet účastníků řízení pro příští notifikaci',
                Found.objects.count()],
        ]