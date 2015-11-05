# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0010_auto_20150805_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='nr_results',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
    ]
