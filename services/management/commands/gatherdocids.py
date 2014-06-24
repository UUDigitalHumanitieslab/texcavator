#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gather document ids of documents in the index and store them in the
database. The collection of document ids is used for testing ElasticSearch
performance on term aggregations (command: esperformance).
"""
from django.core.management.base import BaseCommand
from django.conf import settings

from services.es import _es
from services.models import DocID


class Command(BaseCommand):
    args = '<#-of-document-ids>'
    help = 'Gathers #-of-document-ids from the ElasticSearch index. The ' \
           'collection of document ids is used to test ElastiSearch ' \
           'performance.'

    def handle(self, *args, **options):
        n_document_ids = 100000
        if len(args) > 0:
            n_document_ids = int(args[0])

        match_all = {'query': {'match_all': {}}}

        total_docs = _es().count(settings.ES_INDEX,
                                 settings.ES_DOCTYPE,
                                 match_all).get('count', 0)

        if n_document_ids > total_docs:
            n_document_ids = total_docs

        # Empty database
        DocID.objects.all().delete()

        self.stdout.write('Retrieving {num} document ids...'.
                          format(num=n_document_ids))

        fields = []
        get_more_docs = True
        start = 0
        num = 2500
        num_retrieved = 0

        while get_more_docs:
            doc_ids = []
            results = _es().search(index=settings.ES_INDEX,
                                   doc_type=settings.ES_DOCTYPE,
                                   body=match_all,
                                   fields=fields,
                                   from_=start,
                                   size=num)
            for result in results['hits']['hits']:
                num_retrieved = num_retrieved + 1
                d = DocID(doc_id=result['_id'])
                doc_ids.append(d)

                if num_retrieved == n_document_ids:
                    get_more_docs = False

                if num_retrieved % 1000 == 0:
                    self.stdout.write('. ', ending='')
                    self.stdout.flush()

            DocID.objects.bulk_create(doc_ids)
            start = start + num
        self.stdout.write('')
