# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0003_auto_20150506_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='title',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='query',
            unique_together=set([('user', 'title')]),
        ),
    ]
