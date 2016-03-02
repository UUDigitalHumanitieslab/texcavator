import math
import os
import time
from collections import Counter

import dawg

from django.core.management.base import BaseCommand
from django.conf import settings

from query.models import Distribution, Term
from services.es import count_search_results, document_id_chunks, termvector_wordcloud
from texcavator.utils import daterange2dates

TIMEFRAMES = {'pre': '19000101,19400515', 'WWII': '19400516,19450508', 'post': '19450509,19901231'}


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

        for timeframe, dates in TIMEFRAMES.items():
            print 'Retrieving documents for timeframe {}...'.format(timeframe)
            exclude_dist = Distribution.objects.exclude(name='Landelijk').values_list('id', flat=True)
            date_range = daterange2dates(dates)

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
                counter += termvector_wordcloud(settings.ES_INDEX,
                                                settings.ES_DOCTYPE,
                                                s,
                                                min_length=2,
                                                add_freqs=False)
                print 'Completed set {} in {} seconds...'.format(n + 1, time.time() - start_time)

            print 'Calculating IDFs...'
            terms = []
            for term, count in counter.items():
                if count > 1:  # don't add single occurrences
                    idf = math.log10(total_documents / float(count))
                    terms.append(Term(timeframe=timeframe, word=term, count=count, idf=idf))

            print 'Transferring to database...'
            Term.objects.bulk_create(terms, batch_size=10000)

            print 'Creating RecordDAWG'
            d = dawg.RecordDAWG('<d', zip([t.word for t in terms], [(t.idf,) for t in terms]))
            d.save(os.path.join(settings.PROJECT_PARENT, timeframe + '.dawg'))

        """ Test code below.
        print 'Testing DAWG'
        start_time = time.time()
        d = dawg.RecordDAWG('<d')
        d.load('pre.dawg')
        text = 'dit is een test' # replace with something longer
        for word in text.lower().split(' '):
            try:
                print d[word][0][0]
            except KeyError:
                print 1
        print 'Took: {}'.format(time.time() - start_time)

        print 'Testing database'
        start_time = time.time()
        for word in text.lower().split(' '):
            f = 1
            try:
                t = Term.objects.get(word=word)
                f = t.idf
            except Term.DoesNotExist:
                pass
            print f
        print 'Took: {}'.format(time.time() - start_time)
        """
