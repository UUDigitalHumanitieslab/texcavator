#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate word clouds based on termvectors for random sets of documents.
"""
import logging

from django.core.management.base import BaseCommand

from collections import Counter
import time

from services.es import _es
from services.models import DocID
from texcavator import utils

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<#-documents, size-of-ES-chunks, #-repetitions>'
    help = 'Generate word clouds using term vectors. #-documents is the ' \
           'number of documents the word cloud must be generated for. ' \
           'size-of-ES-chunk is the number of documents that is retrieved ' \
           'in each ElasticSearch request. #-repetitions is the number of ' \
           'word cloud generation is repeated (with a new random set of ' \
           'documents).'

    def handle(self, *args, **options):
        query_size = 2500
        n_repetitions = 10
        es_retrieve = 2500

        if len(args) > 0:
            query_size = int(args[0])
        if len(args) > 1:
            n_repetitions = int(args[1])
        if len(args) > 2:
            es_retrieve = int(args[2])

        response_times = []

        for repetition in range(n_repetitions):
            c1 = time.time()
            es_time = []

            wordcloud = Counter()

            # select random documents
            document_set = DocID.objects.order_by('?')[0:query_size]
            doc_ids = [doc.doc_id for doc in document_set]

            for ids in utils.chunks(doc_ids, es_retrieve):

                bdy = {
                    'ids': ids,
                    'parameters': {
                        'fields': ['article_dc_title', 'text_content'],
                        'term_statistics': False,
                        'field_statistics': False,
                        'offsets': False,
                        'payloads': False,
                        'positions': False

                    }
                }

                c3 = time.time()
                t_vectors = _es().mtermvectors(index='kb', doc_type='doc',
                                               body=bdy)
                c4 = time.time()

                es_time.append((c4-c3)*1000)

                for doc in t_vectors.get('docs'):
                    for field, data in doc.get('term_vectors').iteritems():
                        temp = {}
                        for term, details in data.get('terms').iteritems():
                            temp[term] = int(details['term_freq'])
                        wordcloud.update(temp)

            c2 = time.time()

            elapsed_c = (c2-c1)*1000
            response_times.append(elapsed_c)
            self.stdout.write(str(elapsed_c)+' ES: '+str(sum(es_time)))
            self.stdout.flush()

        avg = float(sum(response_times)/len(response_times))
        print 'Average response time for generating word clouds from {num} ' \
              'documents: {avg} miliseconds'.format(num=query_size, avg=avg)
