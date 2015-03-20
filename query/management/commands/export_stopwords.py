#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Export stopwords of selected users.
"""
from django.core.management.base import BaseCommand

from query.models import StopWord
from query.management.commands.export_queries import users

class Command(BaseCommand):
    args = ''
    help = 'Export stopwords'

    def handle(self, *args, **options):
        stopwords = StopWord.objects.all()

        print 'id\tuser_id\tquery_id\tword'

        for s in stopwords:
            if s.user.username in users:
                if s.query:
                    query_id = str(s.query.id)
                else:
                    query_id = ''
                print '\t'.join([str(s.id), str(s.user.id), query_id,
                                 s.word])
