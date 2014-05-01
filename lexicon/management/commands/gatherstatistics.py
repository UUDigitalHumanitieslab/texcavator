#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Daan Odijk, Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/gatherstatistics.py
Version:	0.22
Goal:		Gathers statistics for the total amount of documents from begindate till enddate for every day.
			The document count are taken from the KB SRU
			 -> change this into our own ES
			Empty the db table before starting
Backup:		$ mysqldump --verbose --user=<usr> --password=<pwd> biland lexicon_daystatistic > lexicon_daystatistic-<date>.sql
Restore:	$ mysql biland --user=<usr> --password=<pwd> < lexicon_daystatistic-<date>.sql

			old select count(*) from lexicon_daystatistic; -> 138043
			new select count(*) from lexicon_daystatistic; -> 138061		6.1 MiB 2013.09.11

DO-%%-%%%-2012: Created
FL-11-Sep-2013: Changed
"""

import sys
from datetime import datetime, timedelta
from time import sleep

from celery.task.sets import TaskSet
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from lexicon.models import DayStatistic
from lexicon.tasks import storeSRUResultsCount


class Command(BaseCommand):
    args = '<begindate enddate>'
    help = 'Gathers statistics for the total amount of documents from begindate till enddate for every day.'

    def handle(self, *args, **options):
		begin_num = settings.SRU_DATE_LIMITS_KBALL[ 0 ]
		end_num   = settings.SRU_DATE_LIMITS_KBALL[ 1 ]
		begin = datetime.strptime( str( begin_num ), '%Y%m%d' ).date()
		end   = datetime.strptime( str( end_num ),   '%Y%m%d' ).date()

		if len( args ) > 0:
			begin = datetime.strptime( args[ 0 ], '%Y%m%d').date()
		if len( args ) > 1:
			end   = datetime.strptime( args[ 1 ], '%Y%m%d').date()

		self.stdout.write( 'Gathering statistics from %s till %s.\n' % ( begin, end ) )
	#	sys.exit( 0 )

# 		tasks = [storeSRUResultsCount.subtask([begin])]
# 		job = TaskSet(tasks=tasks)
# 		result = job.apply_async()
		tasks = []
		date = begin
		day = timedelta( days = 1 )
		while date <= end:
			tasks.append( storeSRUResultsCount.subtask( [ date ] ) )
			date += day
			if( len( tasks ) >= 25 ):
				print "Scheduling %d tasks. " % len( tasks )
				result = TaskSet( tasks = tasks ).apply_async()
				tasks = []
				while not result.ready():
					sleep( 10 )

		print "Scheduling %d tasks." % len( tasks )
		job = TaskSet( tasks = tasks )
		result = job.apply_async()
		
		print result.ready()  # have all subtasks completed?
		print result.successful() # were all subtasks successful?
		#print result.join()
		
		for task in result:
			print task

		"""
		Scheduling 13 tasks.
		False
		False
		0
		0
		403
		237
		3
		367
		262
		201
		359
		393
		3
		334
		201
		"""
# [eof]
