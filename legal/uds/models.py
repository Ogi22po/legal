# -*- coding: utf-8 -*-
#
# uds/models.py
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

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.contrib.auth.models import User

from legal.common.glob import REGISTER_RE_STR
from legal.common.utils import composeref
from legal.fulltext.fulltext import SearchManager


class Publisher(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True)

    type = models.CharField(
        max_length=150,
        db_index=True)

    pubid = models.IntegerField(
        validators=(MinValueValidator(1),))

    high = models.BooleanField(
        default=False,
        db_index=True)

    subsidiary_region = models.BooleanField(
        default=False,
        db_index=True)

    subsidiary_county = models.BooleanField(
        default=False,
        db_index=True)

    reports = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL)

    updated = models.DateTimeField(
        null=True,
        db_index=True)

    timestamp_add = models.DateTimeField(
        auto_now_add=True)

    timestamp_update = models.DateTimeField(
        auto_now=True)

    def __str__(self):
        return self.name


class Agenda(models.Model):

    desc = models.CharField(
        max_length=255,
        unique=True)

    timestamp_add = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return self.desc


class Document(models.Model):

    docid = models.IntegerField(
        validators=(MinValueValidator(1),),
        unique=True)

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE)

    desc = models.CharField(
        max_length=255)

    ref = models.CharField(
        max_length=255)

    senate = models.IntegerField(
        null=True,
        validators=(MinValueValidator(0),))

    register = models.CharField(
        null=True,
        max_length=30,
        validators=(RegexValidator(regex=REGISTER_RE_STR),))

    number = models.PositiveIntegerField(
        null=True)

    year = models.IntegerField(
        null=True,
        validators=(MinValueValidator(1950),))

    page = models.PositiveIntegerField(
        null=True)

    agenda = models.ForeignKey(
        Agenda,
        on_delete=models.CASCADE)

    posted = models.DateTimeField(
        db_index=True)

    timestamp_add = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return '{}, {}'.format(self.publisher.name, self.ref)


class File(models.Model):

    fileid = models.IntegerField(
        validators=(MinValueValidator(1),),
        unique=True)

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE)

    name = models.CharField(
        max_length=255)

    text = models.TextField()

    ocr = models.BooleanField(
        default=False,
        db_index=True)

    timestamp_add = models.DateTimeField(
        auto_now_add=True)

    objects = SearchManager(['text'])

    def __str__(self):
        return '{}, {}, {}'.format(self.document.publisher.name, self.document.desc, self.name)
