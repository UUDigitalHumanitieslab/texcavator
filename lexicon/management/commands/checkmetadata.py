#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/checkmetadata.py
Version:	0.1
Goal:		Check the KB Metadata in Django for the type field in DigitaleDagbladenArticle, 
			that can have 1-of-4 values: 
				artikel
				advertentie
				illustratie met onderschrift
				familiebericht
			execute in the $BILAND_HOME directory:
				$ ./manage.py checkmetadata  <query_name>
			if the lexicon name consists of more than 1 word, enclose them in ""

FL-16-Nov-2012: Created
FL-26-Aug-2012: Changed
"""

import datetime
import requests
from time import time
from sys import stderr, exc_info

from django.core.management.base import BaseCommand

from BiLand.lexicon.models import LexiconItem


class Command( BaseCommand ):
	def handle( self, *args, **kwargs ):
		t1 = time()
		self.stdout.write( "checkmetadata\n" )
		self.stdout.write( "%d args\n" % len( args ) )
		for arg in args:
			self.stdout.write( "arg: %s\n" % arg )

		lexicon_title = ''
		if len( args ) == 0:
			self.stdout.write( "no lexicon name specified\n" )
			return
		else:
			lexicon_title = args[ 0 ]
			self.stdout.write( "lexicon_title: %s\n" % lexicon_title )

		lexicons_qset = LexiconItem.objects.select_related().filter( title = lexicon_title )
		nlexicons = lexicons_qset.count()		# instead of len(), when we do not need all hits to be retrieved
		if nlexicons == 0:
			self.stdout.write( "lexicon with title '%s' was not found\n" % lexicon_title )
		elif nlexicons > 1:
			self.stdout.write( "%d lexicons with title %s !\n" % ( nlexicons, lexicon_title ) )

		for lexicon_qset in lexicons_qset:
			if lexicon_title.endswith( "_daterange" ):
				pass
			else:
				self.analyse_metadata( lexicon_qset )

		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


	def analyse_metadata( self, lexicon ):
		title      = lexicon.title
		user       = lexicon.user
		created    = lexicon.created
		ndocuments = lexicon.documents.count()
		self.stdout.write( "analyse_metadata: lexicon: %s\n" % title )

		self.stdout.write( "lexicon '%s' by '%s' was created on %s, containing %d metadata documents\n" % ( title, user, created, ndocuments ) )

		article_count = 0	# "artikel"							regular articles
		advert_count  = 0	# "advertentie"						advertisements
		illust_count  = 0	# "illustratie met onderschrift"	illustration+text
		family_count  = 0	# "familiebericht"					family messages
		unknown_count = 0

		documents = lexicon.documents.all()
		for document in documents:
			dtype = document.type
		#	self.stdout.write( "type: %s\n" % dtype )

			if dtype == "artikel":
				article_count += 1
			elif dtype == "advertentie":
				advert_count += 1
			elif dtype == "illustratie met onderschrift":
				illust_count += 1
			elif dtype == "familiebericht":
				family_count += 1
			else:
				unknown_count += 1

		total_count = article_count + advert_count + illust_count + family_count + unknown_count

		self.stdout.write( "article_count: %d\n" % article_count )
		self.stdout.write( "advert_count:  %d\n" % advert_count )
		self.stdout.write( "illust_count:  %d\n" % illust_count )
		self.stdout.write( "family_count:  %d\n" % family_count )
		self.stdout.write( "unknown_count: %d\n" % unknown_count )
		self.stdout.write( "total_count:   %d\n" % total_count )

# [eof]
