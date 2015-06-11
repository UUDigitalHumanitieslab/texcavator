# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    """Will load the pillars.json fixture"""
    call_command('loaddata', 'pillars', app_label='query')


def unload_fixture(apps, schema_editor):
    """Will delete all existing Pillars"""
    pillar = apps.get_model('query', 'pillar')
    pillar.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0005_auto_20150611_1125'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
