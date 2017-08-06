# -*- coding: utf-8 -*-
# Generated by Django 1.10b1 on 2016-07-07 00:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VATrate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.FloatField()),
                ('valid', models.DateField(db_index=True)),
            ],
        ),
    ]