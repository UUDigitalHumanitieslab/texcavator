"""Reads in a default set of stopwords from a text file for all current users and all queries.
"""
import os

from django.core.management.base import BaseCommand, CommandError

from query.models import StopWord


class Command(BaseCommand):
    args = '<stopword_list...>'
    help = 'Reads in specified lists of (default) stopwords, removes existing set'

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError('No stopword list specified')

        print 'Removing default stopword set...'
        default_stopwords = StopWord.objects.filter(user=None).filter(query=None)
        default_stopwords.delete()

        filenames = []
        for arg in args:
            filenames.append(os.path.join(os.path.dirname(__file__), arg))

        for filename in filenames:
            with open(filename) as f:
                for line in f:
                    StopWord.objects.create(word=line.strip())
                print 'Stopwords from file %s added.' % filename
