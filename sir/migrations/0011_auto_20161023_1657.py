# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-23 16:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sir', '0010_auto_20161022_1626'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='vec',
            index_together=set([('firstAction', 'rocnik', 'bc', 'idOsobyPuvodce')]),
        ),
    ]
