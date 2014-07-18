#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Perform searches with random weighted queries in ElasticSearch.
"""
from random import randint
import time
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

from services.es import do_search, daterange2dates
from services.models import QueryTerm


class Command(BaseCommand):
    args = '<#-query-terms, #-repetitions>'
    help = 'Perform searches with weighted queries in ElasticSearch. ' \
           '#-query-terms is the terms per query. #-repetitions is the ' \
           'number of random weigthed queries that is send to Elasticsearch.'

    def handle(self, *args, **options):
        if QueryTerm.objects.all().count() == 0:
            print 'No query terms stored in the database. Please run ' \
                  'python manage.py gatherqueryterms\' first.'
            sys.exit(1)

        query_size = 10
        n_repetitions = 10

        if len(args) > 0:
            query_size = int(args[0])
        if len(args) > 1:
            n_repetitions = int(args[1])

        response_times = []
        es_wall_clock = []

        for repetition in range(n_repetitions):
            # generate random weigthed query
            query_terms = QueryTerm.objects.order_by('?')[0:query_size]

            query_list = ['{}^{}'.format(t.term, randint(1, 40))
                          for t in query_terms]
            q = ' OR '.join(query_list)

            t1 = time.time()
            valid_q, result = do_search(settings.ES_INDEX, settings.ES_DOCTYPE,
                                        q, 0, 20, daterange2dates(''), [], [])
            t2 = time.time()

            if not valid_q:
                print 'Invalid query: {}'.format(q)
            else:
                es_wall_clock.append((t2-t1)*1000)
                response_times.append(int(result.get('took')))
                self.stdout.write(str(result.get('took')))
                self.stdout.flush()

        avg = float(sum(response_times)/len(response_times))
        avg_wall_clock = float(sum(es_wall_clock)/len(es_wall_clock))
        print 'Average response time for queries of size {}: {} miliseconds'. \
              format(query_size, avg)
        print 'Average wall clock time for queries of size {}: {} ' \
              'miliseconds'.format(query_size, avg_wall_clock)
