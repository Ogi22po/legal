# Generated by Django 2.1.3 on 2018-11-17 07:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uds', '0005_auto_20181117_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='docid',
            field=models.IntegerField(db_index=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
