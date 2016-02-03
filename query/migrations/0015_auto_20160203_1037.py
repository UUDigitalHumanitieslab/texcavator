# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0014_auto_20160202_1655'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='query',
            options={'permissions': (('download_documents', 'Can download results of a query'), ('download_many_documents', 'Can download larger numbers of results'))},
        ),
    ]
