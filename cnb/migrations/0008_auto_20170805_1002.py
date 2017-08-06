# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-05 10:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cnb', '0007_fxcurrrate_timestamp_update'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FXcurrrate',
        ),
        migrations.RemoveField(
            model_name='fxrate',
            name='timestamp_add',
        ),
        migrations.RemoveField(
            model_name='mpirate',
            name='timestamp_add',
        ),
        migrations.AlterField(
            model_name='mpirate',
            name='rate',
            field=models.FloatField(),
        ),
    ]
