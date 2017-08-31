# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-30 07:15
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uds', '0012_fulltext'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='docid',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='file',
            name='fileid',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('docid', 'publisher')]),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('fileid', 'document')]),
        ),
    ]
