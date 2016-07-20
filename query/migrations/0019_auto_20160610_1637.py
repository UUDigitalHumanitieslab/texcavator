# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0018_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='query',
            options={'verbose_name_plural': 'Queries', 'permissions': (('download_documents', 'Can download results of a query'), ('download_many_documents', 'Can download larger numbers of results'))},
        ),
    ]
