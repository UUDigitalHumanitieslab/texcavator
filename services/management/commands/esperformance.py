#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Perform ElasticSearch term aggregations over random sets of documents.

This command requires a set of document ids to be available in the database.
To store these docids, run management command gatherdocids
"""
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from services.es import multiple_document_word_cloud, daterange2dates
from services.models import DocID


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<#-documents, #-repetitions>'
    help = 'Perform ElasticSearch term aggregations. #-documents is the ' \
           'number of documents that are aggregated per query. #-repetitions' \
           ' is the number of number of random document sets that are ' \
           'aggregrated.'

    def handle(self, *args, **options):
        query_size = 100000
        n_repetitions = 10

        if len(args) > 0:
            query_size = int(args[0])
        if len(args) > 1:
            n_repetitions = int(args[1])

        response_times = []

        for repetition in range(n_repetitions):
            # select random documents
            document_set = DocID.objects.order_by('?')[0:query_size]
            doc_ids = [doc.doc_id for doc in document_set]

            aggr_resp = multiple_document_word_cloud(settings.ES_INDEX,
                                                     settings.ES_DOCTYPE,
                                                     None,
                                                     daterange2dates(''),
                                                     [],
                                                     [],
                                                     doc_ids)
            response_times.append(int(aggr_resp.get('took')))
            self.stdout.write(str(aggr_resp.get('took')))
            self.stdout.flush()

        avg = float(sum(response_times)/len(response_times))
        print 'Average response time for aggregating over {num} documents: ' \
              '{avg} miliseconds'.format(num=query_size, avg=avg)
