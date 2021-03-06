# -*- coding: utf-8 -*-
#
# psj/models.py
#
# Copyright (C) 2011-19 Tomáš Pecina <tomas@pecina.cz>
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

from legal.common.glob import REGISTER_RE_STR
from legal.common.utils import composeref
from legal.szr.models import Court


class Courtroom(models.Model):

    court = models.ForeignKey(
        Court,
        on_delete=models.CASCADE)

    desc = models.CharField(
        max_length=255,
        db_index=True)

    timestamp_add = models.DateTimeField(
        auto_now_add=True)

    timestamp_update = models.DateTimeField(
        auto_now=True)

    def __str__(self):
        return '{0.court}, {0.desc}'.format(self)


class Party(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True)

    timestamp_add = models.DateTimeField(
        auto_now_add=True,
        db_index=True)

    def __str__(self):
        return self.name


class Judge(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True)

    timestamp_add = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return self.name


class Form(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True)

    timestamp_add = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return self.name


class Hearing(models.Model):

    courtroom = models.ForeignKey(
        Courtroom,
        on_delete=models.CASCADE)

    time = models.DateTimeField(
        db_index=True)

    senate = models.IntegerField(
        validators=(MinValueValidator(0),))

    register = models.CharField(
        max_length=30,
        validators=(RegexValidator(regex=REGISTER_RE_STR),))

    number = models.PositiveIntegerField()

    year = models.PositiveIntegerField()

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE)

    judge = models.ForeignKey(
        Judge,
        on_delete=models.CASCADE)

    parties = models.ManyToManyField(
        Party)

    closed = models.BooleanField(
        default=False)

    cancelled = models.BooleanField(
        default=False)

    auxid = models.IntegerField(
        default=0)

    timestamp_add = models.DateTimeField(
        auto_now_add=True,
        db_index=True)

    timestamp_update = models.DateTimeField(
        auto_now=True)

    def __str__(self):
        return '{}, {}'.format(
            self.courtroom.court.name,
            composeref(self.senate, self.register, self.number, self.year))


class Task(models.Model):

    court = models.ForeignKey(
        Court,
        on_delete=models.CASCADE)

    date = models.DateField()

    timestamp_add = models.DateTimeField(
        auto_now_add=True,
        db_index=True)
    timestamp_update = models.DateTimeField(
        auto_now=True,
        db_index=True)

    def __str__(self):
        return '{0.court.name}, {0.date}'.format(self)
