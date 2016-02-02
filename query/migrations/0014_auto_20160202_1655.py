# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0013_term'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='query',
            options={'permissions': (('download_many_documents', 'Can download larger numbers of results'),)},
        ),
    ]
