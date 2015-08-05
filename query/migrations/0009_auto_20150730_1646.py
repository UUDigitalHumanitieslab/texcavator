# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def move_dateranges(apps, schema_editor):
    """Will move all date ranges from Query to Period"""
    Query = apps.get_model('query', 'Query')
    Period = apps.get_model('query', 'Period')
    for query in Query.objects.all():
        p = Period(date_lower=query.date_lower, date_upper=query.date_upper, query=query)
        p.save()


def unmove_dateranges(apps, schema_editor):
    """Will move all date ranges from Period back to Query"""
    Query = apps.get_model('query', 'Query')
    Period = apps.get_model('query', 'Period')
    for period in Period.objects.all():
        q = Query.objects.get(pk=period.query.pk)
        q.date_lower = period.date_lower
        q.date_upper = period.date_upper
        q.save()


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0008_auto_20150730_1645'),
    ]

    operations = [
        migrations.RunPython(move_dateranges, reverse_code=unmove_dateranges),
    ]
