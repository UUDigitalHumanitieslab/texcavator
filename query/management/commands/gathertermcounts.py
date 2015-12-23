"""Gather statistics of the total number of terms"""
import math
from collections import Counter

from django.core.management.base import BaseCommand
from django.conf import settings

from query.models import Distribution, Term
from services.es import document_id_chunks, termvector_wordcloud
from texcavator.utils import daterange2dates


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        print 'Emptying table...'
        Term.objects.all().delete()

        exclude_dist = Distribution.objects.exclude(name='Landelijk').values_list('id', flat=True)
        date_range = daterange2dates('19000101,19901231')
        sets = document_id_chunks(1000,
                                  settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  'test',
                                  date_range,
                                  dist=exclude_dist)

        counter = Counter()
        total_documents = 0
        for n, s in enumerate(sets):
            counter += termvector_wordcloud(settings.ES_INDEX, settings.ES_DOCTYPE, s, 4)
            total_documents += len(s)
            if n == 1:
                break

        for term, count in counter.items():
            idf = math.log10(total_documents / float(count))
            t = Term(word=term, count=count, idf=idf)
            t.save()
