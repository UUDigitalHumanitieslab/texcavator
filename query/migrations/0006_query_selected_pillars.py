# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0005_auto_20150611_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='selected_pillars',
            field=models.ManyToManyField(to='query.Pillar', blank=True),
            preserve_default=True,
        ),
    ]
