# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocID',
            fields=[
                ('doc_id', models.CharField(max_length=26, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QueryTerm',
            fields=[
                ('term', models.CharField(max_length=26, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
