# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0016_auto_20160203_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='daystatistic',
            name='article_type',
            field=models.ForeignKey(blank=True, to='query.ArticleType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='daystatistic',
            name='distribution',
            field=models.ForeignKey(blank=True, to='query.Distribution', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='daystatistic',
            name='date',
            field=models.DateField(),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='daystatistic',
            unique_together=set([('date', 'distribution', 'article_type')]),
        ),
    ]
