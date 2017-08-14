# -*- coding: utf-8 -*-
#
# cache/models.py
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
from django.db import models


class Cache(models.Model):

    url = models.URLField(
        db_index=True)

    text = models.TextField()

    expire = models.DateTimeField(
        null=True,
        db_index=True)

    def __str__(self):
        return self.url


class Asset(models.Model):

    sessionid = models.CharField(
        max_length=32)

    assetid = models.CharField(
        max_length=150)

    data = models.TextField()

    expire = models.DateTimeField(
        null=True,
        db_index=True)

    class Meta:
        unique_together = ('sessionid', 'assetid')

    def __str__(self):
        return self.sessionid