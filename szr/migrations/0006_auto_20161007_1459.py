# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 14:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('szr', '0005_auto_20160713_0253'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='proceedings',
            unique_together=set([('desc', 'id')]),
        ),
    ]
