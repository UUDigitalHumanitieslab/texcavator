# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleType',
            fields=[
                ('id', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=35)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DayStatistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(unique=True)),
                ('count', models.IntegerField()),
                ('checked', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=35)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('query', models.TextField()),
                ('date_lower', models.DateField()),
                ('date_upper', models.DateField()),
                ('title', models.TextField()),
                ('comment', models.TextField(blank=True)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('exclude_article_types', models.ManyToManyField(to='query.ArticleType', blank=True)),
                ('exclude_distributions', models.ManyToManyField(to='query.Distribution', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StopWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word', models.CharField(max_length=100)),
                ('query', models.ForeignKey(blank=True, to='query.Query', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
