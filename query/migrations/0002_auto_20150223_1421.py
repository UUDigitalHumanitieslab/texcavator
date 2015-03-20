# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from query.models import ArticleType, Distribution


def add_article_types_and_distributions(apps, schema_editor):
    # article types
    o = ArticleType(id="st_article", name="artikel")
    o.save()

    o = ArticleType(id="st_advert", name="advertentie")
    o.save()

    o = ArticleType(id="st_illust", name="illustratie met onderschrift")
    o.save()

    o = ArticleType(id="st_family", name="familiebericht")
    o.save()

    # distributions
    o = Distribution(id="sd_national", name="Landelijk")
    o.save()

    o = Distribution(id="sd_regional", name="Regionaal/lokaal")
    o.save()

    o = Distribution(id="sd_antilles", name="Nederlandse Antillen")
    o.save()

    o = Distribution(id="sd_surinam", name="Suriname")
    o.save()

    o = Distribution(id="sd_indonesia", name="Nederlands-Indië / Indonesië")
    o.save()


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_article_types_and_distributions),
    ]
