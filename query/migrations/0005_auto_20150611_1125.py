# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0004_auto_20150507_1024'),
    ]

    operations = [
        migrations.CreateModel(
            name='Newspaper',
            fields=[
                ('id', models.CharField(max_length=9, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=500)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('editions', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pillar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='newspaper',
            name='pillar',
            field=models.ForeignKey(to='query.Pillar', null=True),
            preserve_default=True,
        ),
    ]
