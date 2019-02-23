# Generated by Django 2.1.7 on 2019-02-23 10:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dir', '0011_auto_20180614_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debtor',
            name='year_birth_from',
            field=models.SmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2019)]),
        ),
        migrations.AlterField(
            model_name='debtor',
            name='year_birth_to',
            field=models.SmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2019)]),
        ),
    ]
