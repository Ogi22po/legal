# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-14 13:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sir', '0020_auto_20161114_1333'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adresa',
            old_name='timestamp',
            new_name='timestamp_update',
        ),
    ]
