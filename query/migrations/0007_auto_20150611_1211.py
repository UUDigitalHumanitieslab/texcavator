# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def load_fixtures(apps, schema_editor):
    """Will load the pillars.json/newspapers.json fixtures"""
    call_command('loaddata', 'pillars', app_label='query')
    call_command('loaddata', 'newspapers', app_label='query')


def unload_fixtures(apps, schema_editor):
    """Will delete all existing Pillars/Newspapers"""
    pillar = apps.get_model('query', 'pillar')
    pillar.objects.all().delete()

    newspaper = apps.get_model('query', 'newspaper')
    newspaper.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0006_query_selected_pillars'),
    ]

    operations = [
        migrations.RunPython(load_fixtures, reverse_code=unload_fixtures),
    ]
