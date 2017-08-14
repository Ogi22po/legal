# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-07-30 12:00
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('psj', '0002_auto_20160713_0253'),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hearing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(db_index=True)),
                ('senate', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('register', models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(regex='^(T|C|P a Nc|D|E|P|Nc|ERo|Ro|EC|EVC|EXE|EPR|PP|Cm|Sm|Ca|Cad|Az|To|Nt|Co|Ntd|Cmo|Ko|Nco|Ncd|Ncp|ECm|ICm|INS|K|Kv|EVCm|A|Ad|Af|Na|UL|Cdo|Odo|Tdo|Tz|Ncu|Ads|Afs|Ans|Ao|Aos|Aprk|Aprn|Aps|Ars|As|Asz|Azs|Komp|Konf|Kse|Kseo|Kss|Ksz|Na|Nad|Nao|Ncn|Nk|Ntn|Obn|Plen|Plsn|Pst|Rozk|Rs|S|Spr|Sst|Vol)$')])),
                ('number', models.PositiveIntegerField()),
                ('year', models.IntegerField(validators=[django.core.validators.MinValueValidator(1990)])),
                ('closed', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('courtroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psj.Courtroom')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psj.Form')),
            ],
        ),
        migrations.CreateModel(
            name='Judge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='hearing',
            name='judge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psj.Judge'),
        ),
        migrations.AddField(
            model_name='hearing',
            name='parties',
            field=models.ManyToManyField(to='psj.Party'),
        ),
    ]