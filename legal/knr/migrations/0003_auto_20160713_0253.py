# -*- coding: utf-8 -*-
# Generated by Django 1.10b1 on 2016-07-13 02:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('knr', '0002_vatrate'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='car',
            unique_together=set([('uid', 'abbr')]),
        ),
        migrations.AlterUniqueTogether(
            name='formula',
            unique_together=set([('uid', 'abbr')]),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('uid', 'abbr')]),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together=set([('formula', 'fuel')]),
        ),
    ]
