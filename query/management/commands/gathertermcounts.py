import math
import time
from collections import Counter

from django.core.management.base import BaseCommand
from django.conf import settings

from query.models import Distribution, Term
from services.es import count_search_results, document_id_chunks, termvector_wordcloud
from texcavator.utils import daterange2dates


class Command(BaseCommand):
    """
    Gathers the total counts of terms in the index.
    This can be used to normalize for inverse document frequencies in word clouds
    """
    args = ''
    help = 'Gather term counts in the complete index. Make sure ElasticSearch is running!'

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

        sets = document_id_chunks(10000,
                                  settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  None,
                                  date_range,
                                  dist=exclude_dist)

        print 'Counting terms...'
        counter = Counter()
        for n, s in enumerate(sets):
            start_time = time.time()
            counter += termvector_wordcloud(settings.ES_INDEX, settings.ES_DOCTYPE, s, min_length=2)
            print 'Completed set {} in {} seconds...'.format(n + 1, time.time() - start_time)

        print 'Calculating IDFs...'
        terms = []
        for term, count in counter.items():
            if count > 1:  # don't add single occurrences
                idf = math.log10(total_documents / float(count))
                terms.append(Term(word=term, count=count, idf=idf))

        print 'Transferring to database...'
        Term.objects.bulk_create(terms, batch_size=10000)
