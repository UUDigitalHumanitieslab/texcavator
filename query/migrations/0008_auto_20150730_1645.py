# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0007_auto_20150611_1211'),
    ]

    operations = [
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_lower', models.DateField()),
                ('date_upper', models.DateField()),
                ('query', models.ForeignKey(to='query.Query')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
