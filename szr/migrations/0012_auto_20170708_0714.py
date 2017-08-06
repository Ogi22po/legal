# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-08 07:14
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('szr', '0011_auto_20161117_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proceedings',
            name='register',
            field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(regex='^(T|C|P a Nc|D|E|P|Nc|ERo|Ro|EC|EVC|EXE|EPR|PP|Cm|Sm|Ca|Cad|Az|To|Nt|Co|Ntd|Cmo|Ko|Nco|Ncd|Ncp|ECm|ICm|INS|K|Kv|EVCm|A|Ad|Af|Na|UL|Cdo|Odo|Tdo|Tz|Ncu|Ads|Afs|Ans|Ao|Aos|Aprk|Aprn|Aps|Ars|As|Asz|Azs|Komp|Konf|Kse|Kseo|Kss|Ksz|Na|Nad|Nao|Ncn|Nk|Ntn|Obn|Plen|Plsn|Pst|Rozk|Rs|S|Spr|Sst|Vol|Tm|Tmo|Ntm)$')]),
        ),
    ]
