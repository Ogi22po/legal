# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-24 07:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dir', '0009_auto_20170329_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='debtor',
            name='notify',
            field=models.BooleanField(default=False),
        ),
    ]
