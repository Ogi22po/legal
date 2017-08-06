# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-14 14:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('szr', '0008_auto_20161111_0333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proceedings',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='proceedings',
            name='timestamp_add',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proceedings',
            name='timestamp_update',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
