# -*- coding: utf-8 -*-
# Generated by Django 1.10b1 on 2016-07-13 02:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('szr', '0005_auto_20160713_0253'),
        ('psj', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='courtroom',
            unique_together=set([('court', 'name')]),
        ),
    ]
