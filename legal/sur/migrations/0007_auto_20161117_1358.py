# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-17 13:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sur', '0006_auto_20161114_1427'),
    ]

    operations = [
        migrations.RenameField(
            model_name='found',
            old_name='timestamp',
            new_name='timestamp_add',
        ),
    ]
