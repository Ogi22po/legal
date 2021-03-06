# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-09 03:04
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sir', '0004_auto_20161009_0217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adresa',
            name='mesto',
            field=models.CharField(db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='adresa',
            name='psc',
            field=models.CharField(db_index=True, max_length=5, null=True, validators=[django.core.validators.RegexValidator(regex='\\d{5}')]),
        ),
        migrations.AlterField(
            model_name='osoba',
            name='datumNarozeni',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='osoba',
            name='dic',
            field=models.CharField(db_index=True, max_length=14, null=True),
        ),
        migrations.AlterField(
            model_name='osoba',
            name='ic',
            field=models.CharField(db_index=True, max_length=9, null=True, validators=[django.core.validators.RegexValidator(regex='\\d{1,9}')]),
        ),
        migrations.AlterField(
            model_name='osoba',
            name='jmeno',
            field=models.CharField(db_index=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='osoba',
            name='nazevOsoby',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='osoba',
            name='rc',
            field=models.CharField(db_index=True, max_length=10, null=True, validators=[django.core.validators.RegexValidator(regex='\\d{9,10}')]),
        ),
        migrations.AlterField(
            model_name='vec',
            name='datumVyskrtnuti',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='vec',
            name='firstAction',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='vec',
            name='lastAction',
            field=models.DateField(db_index=True),
        ),
    ]
