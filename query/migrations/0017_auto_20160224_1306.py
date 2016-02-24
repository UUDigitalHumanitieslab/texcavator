# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from query.operations import engine_specific


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0016_auto_20160203_1324'),
    ]

    operations = [
        engine_specific(('mysql',),
            migrations.RunSQL(
                'alter table query_term modify word varchar(200) character set utf8 collate utf8_bin;',
                'alter table query_term modify word varchar(200) character set utf8 collate utf8_general_ci;'
            )
        ),
    ]
