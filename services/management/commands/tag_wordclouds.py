#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate word clouds based on words added as tags for random sets of
documents.
"""
import logging

from django.core.management.base import BaseCommand

import time

from services.es import _es
from services.models import DocID


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<#-documents, #-repetitions>'
    help = 'Generate word clouds using words that were added as tags. ' \
           '#-documents is the number of documents the word cloud must be ' \
           'generated for. #-repetitions is the number of times ' \
           'word cloud generation is repeated (with a new random set of ' \
           'documents).'

    def handle(self, *args, **options):
        query_size = 2500
        n_repetitions = 10

        if len(args) > 0:
            query_size = int(args[0])
        if len(args) > 1:
            n_repetitions = int(args[1])

        response_times = []

        for repetition in range(n_repetitions):
            c1 = time.time()
            es_time = []

            # select random documents
            document_set = DocID.objects.order_by('?')[0:query_size]
            doc_ids = [doc.doc_id for doc in document_set]

            if len(doc_ids) == 0:
                print 'No document ids found.\nPlease run the gatherdocids ' \
                      'command first.\n\n'

            query = {
                "query": {
                    "filtered": {
                        "filter": {
                            "ids": {
                                "values": doc_ids
                            }
                        }
                    }
                },
                "aggs": {
                    "words": {
                        "terms": {
                            "field": "tags",
                            "size": 100
                        }
                    }
                },
                "size": 0
            }

            c3 = time.time()
            result = _es().search(index='kb', doc_type='doc', body=query)
            wordcloud = result.get('aggregations').get('words').get('buckets')
            c4 = time.time()

            c2 = time.time()

            elapsed_c = (c2-c1)*1000
            response_times.append(elapsed_c)
            es_time.append((c4-c3)*1000)

            self.stdout.write(str(elapsed_c)+' ES: '+str(sum(es_time)) +
                              ' #results: '+str(len(wordcloud)))
            self.stdout.flush()

        avg = float(sum(response_times)/len(response_times))
        print 'Average response time for generating word clouds from {num} ' \
              'documents: {avg} miliseconds'.format(num=query_size, avg=avg)
