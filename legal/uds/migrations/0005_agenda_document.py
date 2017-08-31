# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-27 15:54
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('uds', '0004_publisher_updated'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agenda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(max_length=255, unique=True)),
                ('timestamp_add', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(max_length=255)),
                ('ref', models.CharField(max_length=255)),
                ('senate', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('register', models.CharField(max_length=30, null=True, validators=[django.core.validators.RegexValidator(regex='^(T|C|P a Nc|D|E|P|Nc|ERo|Ro|EC|EVC|EXE|EPR|PP|Cm|Sm|Ca|Cad|Az|To|Nt|Co|Ntd|Cmo|Ko|Nco|Ncd|Ncp|ECm|ICm|INS|K|Kv|EVCm|A|Ad|Af|Na|UL|Cdo|Odo|Tdo|Tz|Ncu|Ads|Afs|Ans|Ao|Aos|Aprk|Aprn|Aps|Ars|As|Asz|Azs|Komp|Konf|Kse|Kseo|Kss|Ksz|Na|Nad|Nao|Ncn|Nk|Ntn|Obn|Plen|Plsn|Pst|Rozk|Rs|S|Spr|Sst|Vol|Tm|Tmo|Ntm)$')])),
                ('number', models.PositiveIntegerField(null=True)),
                ('year', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1990)])),
                ('posted', models.DateTimeField(db_index=True)),
                ('timestamp_add', models.DateTimeField(auto_now_add=True)),
                ('agenda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uds.Agenda')),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uds.Publisher')),
            ],
        ),
    ]
