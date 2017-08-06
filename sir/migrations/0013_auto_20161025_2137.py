# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 21:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sir', '0012_insolvency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tracked',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(db_index=True, max_length=255)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sir.Vec')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='insolvency',
            index_together=set([('number', 'year')]),
        ),
    ]
