#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gather query terms and store them in the database. The collection of terms 
is used for testing ElasticSearch performance on weighted queries (command: 
weighted_queries).
"""
from django.core.management.base import BaseCommand
from django.conf import settings

from services.es import _es
from services.models import DocID, QueryTerm 
from texcavator import utils


class Command(BaseCommand):
    args = '<#-documents>'
    help = 'Gathers terms used in the titles of #-documets from the ' \
           'ElasticSearch index. The terms are used to test performance of ' \
           'weigthed queries.'

    def handle(self, *args, **options):
        query_size = 10000
        es_retrieve = 2500

        if len(args) > 0:
            query_size = int(args[0])

        if DocID.objects.all().count() == 0:
            print 'Document ids must be gathered before query terms can be ' \
                  'extracted. \n Please execute python manage.py gatherdocids'
            sys.exit(1)

        match_all = {'query': {'match_all': {}}}

        # Empty database
        QueryTerm.objects.all().delete()

        self.stdout.write('Retrieving {} documents...'.format(query_size))

        terms = set() 

        # select random documents
        document_set = DocID.objects.order_by('?')[0:query_size]
        doc_ids = [doc.doc_id for doc in document_set]

        for ids in utils.chunks(doc_ids, es_retrieve):
            bdy = {
                'ids': ids,
                'parameters': {
                    'fields': ['article_dc_title'],
                    'term_statistics': False,
                    'field_statistics': False,
                    'offsets': False,
                    'payloads': False,
                    'positions': False
                }
            }

            t_vectors = _es().mtermvectors(index=settings.ES_INDEX,
                                           doc_type=settings.ES_DOCTYPE,
                                           body=bdy)

            for doc in t_vectors.get('docs'):
                for field, data in doc.get('term_vectors').iteritems():
                    for term, details in data.get('terms').iteritems():
                        t = term.encode('ascii', 'replace')
                        if len(t) <= 26:
                            terms.add(QueryTerm(t))

        # save to database
        print 'Saving {} terms to the database.'.format(len(terms))

        QueryTerm.objects.bulk_create(terms)
