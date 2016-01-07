"""Gather statistics of the total number of terms"""
import math
from collections import Counter

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from query.models import Distribution, Term
from services.es import count_search_results, document_id_chunks, termvector_wordcloud
from texcavator.utils import daterange2dates


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        print 'Emptying table...'
        Term.objects.all().delete()

        print 'Retrieving documents...'
        exclude_dist = Distribution.objects.exclude(name='Landelijk').values_list('id', flat=True)
        date_range = daterange2dates('19000101,19901231')

        total_documents = count_search_results(settings.ES_INDEX,
                                               settings.ES_DOCTYPE,
                                               None,
                                               date_range,
                                               exclude_dist, [], []).get('count')
        print 'Total documents: {}'.format(total_documents)

        sets = document_id_chunks(settings.QUERY_DATA_CHUNK_SIZE,
                                  settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  None,
                                  date_range,
                                  dist=exclude_dist)

        print 'Counting terms...'
        counter = Counter()
        for n, s in enumerate(sets):
            print 'At set {}...'.format(n)
            counter += termvector_wordcloud(settings.ES_INDEX, settings.ES_DOCTYPE, s, min_length=4)
            if n == 10:
                break

        print 'Calculating IDFs...'
        terms = []
        for term, count in counter.items():
            idf = math.log10(total_documents / float(count))
            terms.append(Term(word=term, count=count, idf=idf))
        Term.objects.bulk_create(terms)

        print 'Deleting all terms with frequency of 1...'
        Term.objects.filter(count=1).delete()
