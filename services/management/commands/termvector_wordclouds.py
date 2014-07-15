#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate word clouds based on termvectors for random sets of documents.
"""
from django.core.management.base import BaseCommand
from django.conf import settings

from collections import Counter
import time

from services.es import _es 
from services.models import DocID


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class Command(BaseCommand):
    args = '<#-documents, #-repetitions>'
    help = 'Perform ElasticSearch term aggregations. #-documents is the ' 

    def handle(self, *args, **options):
        query_size = 1000
        n_repetitions = 10

        if len(args) > 0:
            query_size = int(args[0])
        if len(args) > 1:
            n_repetitions = int(args[1])

        response_times = []

        for repetition in range(n_repetitions):
            c1 = time.time()
            t1 = time.clock()
            es_time = []
            
            wordcloud = Counter()

            es_retrieve = 2500

            # select random documents
            document_set = DocID.objects.order_by('?')[0:query_size]
            doc_ids = [doc.doc_id for doc in document_set]

            for ids in chunks(doc_ids, es_retrieve):
                
                bdy = {
                    'ids': ids,
                    'parameters': {
                        'fields': ['article_dc_title', 'text_content'],
                        'term_statistics': False,
                        'field_statistics': False,
                        'offsets' : False,
                        'payloads' : False,
                        'positions' : False

                    }
                }

                c3 = time.time()
                t3 = time.clock()
                t_vectors = _es().mtermvectors(index='kb', doc_type='doc',
                                               body=bdy)
                t4 = time.clock()
                c4 = time.time()

                es_time.append((c4-c3)*1000)
                #print t_vectors

                for doc in t_vectors.get('docs'):
                    #d = {k:v['term_freq'] for k, v in doc.get('term_vectors').get('article_dc_title').get('terms').iteritems()}
                    #e = {k:v['term_freq'] for k, v in doc.get('term_vectors').get('text_content').get('terms').iteritems()}
                    #wordcloud.update(d)
                    #wordcloud.update(e)
                    for field, data in doc.get('term_vectors').iteritems():
                        temp = {}
                        for term, details in data.get('terms').iteritems():
                            temp[term] = int(details['term_freq'])
                        wordcloud.update(temp)

            t2 = time.clock()
            c2 = time.time()

            elapsed = (t2-t1) * 1000
            elapsed_c = (c2-c1)*1000
            response_times.append(elapsed_c)
            #self.stdout.write(str(elapsed)+' ES: '+str((t4-t3)*1000))
            self.stdout.write(str(elapsed_c)+' ES: '+str(sum(es_time)))
            self.stdout.flush()

        avg = float(sum(response_times)/len(response_times))
        print 'Average response time for generating word clouds from {num} ' \
              'documents: {avg} miliseconds'.format(num=query_size, avg=avg)
