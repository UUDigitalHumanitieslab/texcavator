#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/chownlexica.py
Version:	0.1
Goal:		Set or change the ownership of lexica to <user_name>. 
			execute in the $BILAND_HOME directory:
				$ ./manage.py chownlexica <user_name> <lexicon_name>
			if the lexicon name consists of more than 1 word, enclose them in ""
			if the lexicon name consists of a single quoted '*' all lexica are affected
Notice:		group is not yet used, but set to "biland"

FL-15-Feb-2012: Created
FL-26-Aug-2013: Changed
"""

import datetime
import requests
from time import time
from sys import stderr, exc_info


try:
	from lxml import etree
	print >> stderr, "running with lxml.etree"
except ImportError:
	try:
		# Python 2.5
		import xml.etree.cElementTree as etree
		print >> stderr, "running with cElementTree on Python 2.5+"
	except ImportError:
		try:
			# Python 2.5
			import xml.etree.ElementTree as etree
			print >> stderr, "running with ElementTree on Python 2.5+"
		except ImportError:
			try:
				# normal cElementTree install
				import cElementTree as etree
				print >> stderr, "running with cElementTree"
			except ImportError:
				try:
					# normal ElementTree install
					import elementtree.ElementTree as etree
					print >> stderr, "running with ElementTree"
				except ImportError:
					print >> stderr, "Failed to import ElementTree from any known place"

try:
	import json						# Python-2.6+
except:
	import django.utils.simplejson as json

from django.core.management.base import BaseCommand

from BiLand.lexicon.models import LexiconItem


class Command( BaseCommand ):
	def handle( self, *args, **kwargs ):
		t1 = time()
		self.stdout.write( "chownlexica\n" )
		self.stdout.write( "%d args\n" % len( args ) )
		for arg in args:
			self.stdout.write( "arg: %s\n" % arg )

		new_user  = ''
		new_group = "biland"
		lexicon_title = ''
		if len( args ) == 0:
			self.stdout.write( "no parameters specified\n" )
			return
		elif len( args ) == 1:
			self.stdout.write( "only one parameter specified\n" )
			return
		elif len( args ) > 2:
			self.stdout.write( "too many parameters specified\n" )
			return
		else:
			new_user = args[ 0 ]
			lexicon_title = args[ 1 ]
			self.stdout.write( "new owner: %s\n" % new_user )
			self.stdout.write( "lexicon title: %s\n" % lexicon_title )

		if lexicon_title == '*':
			lexicons_qset = LexiconItem.objects.select_related().all()
		else:
			lexicons_qset = LexiconItem.objects.select_related().filter( title = lexicon_title )

		nlexicons = lexicons_qset.count()		# instead of len(), when we do not need all hits to be retrieved
		if nlexicons == 0:
			self.stdout.write( "lexicon with title '%s' was not found\n" % lexicon_title )
		elif nlexicons > 1:
			self.stdout.write( "%d lexicons matching title %s\n" % ( nlexicons, lexicon_title ) )

		for lexicon_qset in lexicons_qset:
			old_user  = lexicon_qset.user
			old_group = lexicon_qset.group
			if old_user == new_user and old_group == new_group:
				self.stdout.write( "skipping lexicon: %s\n" % lexicon_qset.title )
				continue

			self.stdout.write( "changing lexicon: %s, owner: %s -> %s, group: %s -> %s\n" % 
			( lexicon_qset.title, old_user, new_user, old_group, new_group ) )
			lexicon_qset.user  = new_user
			lexicon_qset.group = new_group
			lexicon_qset.save()

		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


# [eof]
