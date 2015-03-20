#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gather statistics of the total number of documents per day and put them in
the database.
"""
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import DatabaseError
from django.conf import settings

from query.models import DayStatistic
from services.es import daterange2dates, day_statistics


class Command(BaseCommand):
    args = '<year2 year2>'
    help = 'Gathers statistics for the total amount of documents from ' \
           'year1 until year2 for every day.'

    def handle(self, *args, **options):
        print 'Emptying table...'
        DayStatistic.objects.all().delete()

        date_range_str = settings.TEXCAVATOR_DATE_RANGE
        dates = daterange2dates(date_range_str)

        year_lower = datetime.strptime(dates['lower'], '%Y-%m-%d').date().year
        year_upper = datetime.strptime(dates['upper'], '%Y-%m-%d').date().year

        if len(args) > 0:
            year_lower = int(args[0])
        if len(args) > 1:
            year_upper = int(args[1])

        print 'Gathering statistics from %s until %s.' \
            % (year_lower, year_upper)

        agg_name = 'daystatistic'

        for year in range(year_lower, year_upper+1):
            date_range = {
                'lower': '{y}-01-01'.format(y=year),
                'upper': '{y}-12-31'.format(y=year)
            }

            print year

            results = day_statistics(settings.ES_INDEX,
                                     settings.ES_DOCTYPE,
                                     date_range,
                                     agg_name)

            if results:
                # save results to database
                agg_data = results['aggregations'][agg_name]['buckets']

                for date in agg_data:
                    try:
                        d = datetime.strptime(date['key_as_string'],
                                              '%Y-%m-%dT00:00:00.000Z').date()
                        DayStatistic.objects.create(date=str(d),
                                                    count=date['doc_count'])
                    except DatabaseError, exc:
                        msg = "Database Error: %s" % exc
                        if settings.DEBUG:
                            print msg
