# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 21:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20161117_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=30, unique_for_date='valid')),
                ('value', models.FloatField()),
                ('valid', models.DateField(db_index=True)),
            ],
        ),
    ]
