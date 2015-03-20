#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Export queries and associated metadata of selected users.
"""
from django.core.management.base import BaseCommand

from query.models import Query

# users that gave permission to export their queries
users = ['jdekruif', 'jesperverhoef', 'mwevers', 'lwalma', 'mvdbos',
         'hhuistra']


class Command(BaseCommand):
    args = ''
    help = 'Export queries'

    def handle(self, *args, **options):
        queries = Query.objects.all()

        print 'id\tquery\tdate_lower\tdate_upper\texclude_article_type\texclude_distributions\tuser_id'

        for q in queries:
            if q.user.username in users:
                excl_art_types = [a.id for a in q.exclude_article_types.all()]
                excl_dist = [d.id for d in q.exclude_distributions.all()]

                print '\t'.join([str(q.id), q.query, str(q.date_lower),
                                str(q.date_upper), '+'.join(excl_art_types),
                                '+'.join(excl_dist), str(q.user.id)])
