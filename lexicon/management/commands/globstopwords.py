#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/globstopwords.py
Version:	0.1
Goal:		Add the list of global stopwords to the stopwords table
				$ ./manage.py globstopwords

FL-28-Nov-2012: Created
FL-26-Aug-2013: Changed
"""

import sys
from datetime import datetime, timedelta
from time import time, sleep
from sys import stderr, exc_info

from django.core.management.base import BaseCommand

from lexicon.models import StopWord


STOPWORDS = "apos,quot,0,1,2,3,4,5,6,7,8,9,10,11,000,_,__,den,de,in,ter,ten"


class Command( BaseCommand ):
	def handle( self, *args, **kwargs ):
		t1 = time()
		self.stdout.write( "globstopwords\n" )
		self.stdout.write( "%d args\n" % len( args ) )
		for arg in args:
			self.stdout.write( "arg: %s\n" % arg )

		self.process_stopwords( STOPWORDS )


		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


	def process_stopwords( self, stopwords_str ):
		self.stdout.write( "stopwords_str: %s\n" % stopwords_str )
		stopwords_list = stopwords_str.split( ',' )
	#	print >> stderr, stopwords_list

		for i in range( len( stopwords_list ) ):
			stopword = stopwords_list[ i ]
			self.stdout.write( "%d: %s\n" % ( i, stopword ) )

			# does this stopword already exist 'globally'?
			try:
				qset = StopWord.objects.all().filter( user = None, query = None, word = stopword )
				wordcount = qset.count()
			#	print >> stderr, "count:", wordcount
				if wordcount == 0:
					self.stdout.write( "stopword '%s' does not exist for all users and all queries\n" % stopword )
					self.save_stopword( stopword )
				else:
					self.stdout.write( "stopword '%s' already exists for all users and all queries\n" % stopword )
			except:
				type, value, tb = exc_info()
				self.stdout.write( "stopword '%s' could not be saved: %s\n" % ( stopword, value.message ) )


	def save_stopword( self, stopword ):
		self.stdout.write( "saving stopword '%s' for all users and all queries\n" % stopword )

		stopwordItem       = StopWord()
		stopwordItem.user  = None
		stopwordItem.query = None
		stopwordItem.word  = stopword

		try:
			stopwordItem.save()
			self.stdout.write( "stopword '%s' has been saved\n" % stopword )
		except:
			type, value, tb = exc_info()
			self.stdout.write( "stopword '%s' could not be saved: %s\n" % ( stopword, value.message ) )

# [eof]
