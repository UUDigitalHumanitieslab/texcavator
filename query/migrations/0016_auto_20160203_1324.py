# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0015_auto_20160203_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='term',
            name='timeframe',
            field=models.CharField(default='pre', max_length=4, choices=[(b'pre', b'pre-WWII: 1900-1940'), (b'WWII', b'WWII: 1940-1945'), (b'post', b'post-WWII: 1945-1990')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='term',
            name='word',
            field=models.CharField(max_length=200),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='term',
            unique_together=set([('timeframe', 'word')]),
        ),
    ]
