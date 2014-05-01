#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/listtags.py
Version:	0.1
Goal:		List articles + their tags for given xTAS key
			execute in the $BILAND_HOME directory:
				$ ./manage.py listtags
			If the option 'check' is provided 
				$ ./manage.py listtags check
			it will check KB articles that have ids that start with "ddd:...". 
			KB articles must have at least 1 tag: ddd

FL-13-Jun-2012: Created
FL-26-Aug-2013: Changed
"""

import datetime
import requests
from time import time
from sys import stderr, exc_info

try:
	import json						# Python-2.6+
except:
	import django.utils.simplejson as json

from django.conf import settings
from django.core.management.base import BaseCommand


class Command( BaseCommand ):
	def handle( self, *args, **kwargs ):
		t1 = time()
		self.stdout.write( "listtags\n" )
		self.stdout.write( "%d args\n" % len( args ) )
		for arg in args:
			self.stdout.write( "arg: %s\n" % arg )

		if len( args ) == 1:
			arg = args[ 0 ]
			if arg == "check":
				check = True
			else:
				check = False
		else:
			check = False
		self.list_articles( check )

		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


	def list_articles( self, check ):
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc"
		else:
			xtas_url = xtas_baseurl + "/doc"
	#	self.stdout.write( xtas_url )

		# get article data from xTAS
	#	lexicon_tag = "Lexicon" + str( lexicon_id )
	#	params = { 'key' : settings.XTAS_API_KEY, 'tags' : lexicon_tag }
		params = { 'key' : settings.XTAS_API_KEY }

		try:
			response = requests.get( xtas_url, params = params )
			content = response.content
		except:
			self.stdout.write( "url: %s" % xtas_url )
			self.stdout.write( "params: %s" % params )
			type, value, tb = exc_info()
			self.stdout.write( "xTas request failed: %s" % value.message )
			content = ""
			article_count = 0

	#	self.stdout.write( content )
		json_resp = json.loads( content )
		status = json_resp[ "status" ]
		if status == "error":
			self.stdout.write( "code: %s, eror: %s\n" % ( json_resp[ "code" ], json_resp[ "error" ] ) )
			return

		result = json_resp[ "result" ]
		count  = int( result[ "count" ] )
		ids    = result[ "ids" ]

		self.stdout.write( "response status: %s\n" % status )
		self.stdout.write( "article count: %d\n" % count )
		if status != "ok":
			return

		ntags_zero = 0
		ntagsddd_zero = 0
		for i in range( count ):
			id = ids[ i ]
			params = { 'key' : settings.XTAS_API_KEY, 'id' : id }
			try:
				response = requests.get( xtas_url, params = params )
				content = response.content
			except:
				self.stdout.write( "url: %s\n" % xtas_url )
				self.stdout.write( "params: %s\n" % params )
				type, value, tb = exc_info()
				self.stdout.write( "xTas request failed: %s\n" % value.message )
				content = ""

		#	self.stdout.write( content )

			json_resp = json.loads( content )
			status = json_resp[ "status" ]

			if status != "ok":
				return

			result = json_resp[ "result" ]
			document = result[ "document" ]
			tags = document[ "tags" ]
			ntags = len( tags )

			self.stdout.write( "%d: id: %s ntags: %d tags: %s\n" % ( i, id, ntags, tags ) )

			created = document[ "created" ]
			updated = document[ "updated" ]
			if created == updated:
				self.stdout.write( "created: %s\n" % ( created ) )
			else:
				self.stdout.write( "created: %s, updated: %s\n" % ( created, updated ) )

			self.stdout.write( "content:\n%s\n" % document[ "content" ].encode( "utf8" ) )

			if ntags == 0:
				ntags_zero += 1
				if check and id.startswith( "ddd:" ):
					ntagsddd_zero += 1

		if check:
			self.stdout.write( "%d documents with 0 tags, of which %d KB articles\n" % ( ntags_zero, ntagsddd_zero ) )
		else:
			self.stdout.write( "%d documents with 0 tags\n" % ntags_zero )

# [eof]
