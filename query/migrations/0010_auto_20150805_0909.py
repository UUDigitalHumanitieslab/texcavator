# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0009_auto_20150730_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='date_lower',
            field=models.DateField(default=date.today),
        ),
        migrations.RemoveField(
            model_name='query',
            name='date_lower',
        ),
        migrations.AlterField(
            model_name='query',
            name='date_upper',
            field=models.DateField(default=date.today),
        ),
        migrations.RemoveField(
            model_name='query',
            name='date_upper',
        ),
    ]
