# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-05 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sir', '0017_auto_20161029_2347'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Error',
        ),
        migrations.AddField(
            model_name='transaction',
            name='error',
            field=models.BooleanField(default=False),
        ),
    ]
