# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0012_auto_20151105_1638'),
    ]

    operations = [
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word', models.CharField(unique=True, max_length=200)),
                ('count', models.PositiveIntegerField()),
                ('idf', models.DecimalField(max_digits=7, decimal_places=4)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
