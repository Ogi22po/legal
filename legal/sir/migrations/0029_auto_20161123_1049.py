# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-23 10:49
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sir', '0028_auto_20161117_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adresa',
            name='psc',
            field=models.CharField(db_index=True, max_length=5, null=True, validators=[django.core.validators.RegexValidator(regex='^\\d{5}$')]),
        ),
        migrations.AlterField(
            model_name='insolvency',
            name='year',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(2008)]),
        ),
        migrations.AlterField(
            model_name='osoba',
            name='ic',
            field=models.CharField(db_index=True, max_length=9, null=True, validators=[django.core.validators.RegexValidator(regex='^\\d{1,9}$')]),
        ),
        migrations.AlterField(
            model_name='osoba',
            name='rc',
            field=models.CharField(db_index=True, max_length=10, null=True, validators=[django.core.validators.RegexValidator(regex='^\\d{9,10}$')]),
        ),
    ]
