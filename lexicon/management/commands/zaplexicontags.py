#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/zaplexicontags.py
Version:	0.11
Goal:		Delete tag[s] from articles
			execute in the $BILAND_HOME directory:
				$ ./manage.py zaplexicontags tag
				$ ./manage.py zaplexicontags tag1,tag2,tag3

FL-13-Dec-2011: Created
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
		self.stdout.write( "zaplexicontags\n" )
		self.stdout.write( "%d args\n" % len( args ) )
		for arg in args:
			self.stdout.write( "arg: %s\n" % arg )

		tags_str = ''
		if len( args ) == 0:
			self.stdout.write( "no tags string specified\n" )
			return
		else:
			tags_str = args[ 0 ]
			self.stdout.write( "tags string: %s\n" % tags_str )
			tag_list = tags_str.split( ',' )

		docid_list = self.get_docids( tags_str )

		self.zaptags( docid_list, tag_list )

		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


	def get_docids( self, tags_str ):
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc"
		else:
			xtas_url = xtas_baseurl + "/doc"
		self.stdout.write( "xTAS url: %s\n" % xtas_url )

		# get docids from xTAS
		params = { 'key' : settings.XTAS_API_KEY, 'tags' : tags_str }

		try:
			response = requests.get( xtas_url, params = params )
		except:
			self.stderr.write( "url: %s" % xtas_url )
			self.stderr.write( "params: %s" % params )
			type, value, tb = exc_info()
			self.stderr.write( "xTAS request failed: %s" % value.messageg )
			article_count = 0

		content = response.content
		self.stdout.write( "content: %s\n" % content )
		if content == "404 No documents found":
			ocrdata_count = 0
		else:
			jsdata = json.loads( response.content )
			status = jsdata[ "status" ]
			if status == "error":
				ocrdata_count = 0
			else:
				ocrdata_count = jsdata[ "result" ][ "count" ]
		self.stdout.write( "ocrdatas: %d\n" % int( ocrdata_count ) )
		docid_list = jsdata[ "result" ][ "ids" ]
		return docid_list


	def zaptags( self, docid_list, tag_list ):
		if len( docid_list ) == 0:
			self.stderr.write( "No docids\n" )
			return

		path = "/doc/removetags"
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + path
		else:
			xtas_url = xtas_baseurl + path

		self.stdout.write( "xTAS url: %s\n" % xtas_url )
		http_config = { 'verbose': stderr }

		ids  = ",".join( docid_list )
		tags = ",".join( tag_list )
		delete = False		# True: delete doc if all tags matched
	#	print >> stderr, ids
		params = { 'key' : settings.XTAS_API_KEY, 'ids' : ids, 'tags' : tags, 'delete' : delete }

		try:
			response = requests.post( xtas_url, data = params, config = http_config )
			content  = response.content
		except:
			self.stderr.write( "url: %s" % xtas_url )
			self.stderr.write( "params: %s" % params )
			type, value, tb = exc_info()
			self.stderr.write( "xTAS request failed: %s" % value.message )
			article_count = 0

		if content == "200 Deleted\n":
			# response XML contains the list of docids that had the tag[s] removed, 
			# so that list may be shorter than the input list
			pass
		else:
			self.stderr.write( "params: %s\n" % params )
			self.stderr.write( "response: %s\n" % content )

# [eof]
