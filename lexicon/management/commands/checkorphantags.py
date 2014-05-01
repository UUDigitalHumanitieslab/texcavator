#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/checkorphantags.py
Version:	0.2
Goal:		Check xTAS docs that have lexicon tags without the lexicon; 
			optionally remove the tag from the documents. 
			Notice: all KB docs have tag 'ddd'
			execute in the $BILAND_HOME directory:
				$ ./manage.py checkorphantags lexiconid <lexicon_id>
				$ ./manage.py checkorphantags lexiconid <lexicon_id> zaptag
				$ ./manage.py checkorphantags lexiconmaxid <lexicon_maxid>
				$ ./manage.py checkorphantags lexiconmaxid <lexicon_maxid> zaptag
				$ ./manage.py checkorphantags ddd
			With lexiconmaxid instead of lexiconid, all lexicons with ids in the 
			range [0...lexiconmaxid] are processed. 
			The 'zagtag' argument only applies to the situation where ocr docs are found, 
			but the corresponding lexicon no longer exists. Then the lexicon tag is 
			removed from those ocr documents. Without the optional 'zaptag' argument, 
			the ocr documents remain unchanged. 
			With the single parameter 'ddd' we check all documents for 'spurious' tags. 
FL-04-Jan-2013: Created
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

from BiLand.lexicon.models import LexiconItem


KBtag = "ddd"


class Command( BaseCommand ):
	def handle( self, *args, **kwargs ):
		t1 = time()
		self.stdout.write( "checkorphantags\n" )
		self.stdout.write( "%d args\n" % len( args ) )
		for arg in args:
			self.stdout.write( "arg: %s\n" % arg )
		if len( args ) == 1:
			check_type = args[ 0 ]
			if check_type != "ddd":
				self.stdout.write( "unrecognized parameter\n" )
				return
		elif len( args ) == 2:
			check_type  = args[ 0 ]
			check_value = args[ 1 ]
			self.stdout.write( "type: %s, value: %s\n" % ( check_type, check_value ) )
			zap_tag = False
		elif len( args ) == 3:
			check_type  = args[ 0 ]
			check_value = args[ 1 ]
			check_zap   = args[ 2 ]
			self.stdout.write( "type: %s, value: %s, zap: %s\n" % ( check_type, check_value, check_zap ) )
			if check_zap != "zaptag":
				self.stdout.write( "unrecognized 3rd parameter: %s\n" % check_zap )
				return
			else:
				zap_tag = True
		else:
			self.stdout.write( "specify parameters: <type> <value> [zaptag]\n" )
			return

	#	tag = KBtag			# default KB historic newspaper tag
		if check_type == "lexiconid":
			lexicon_id = int( check_value )
			self.process_single( lexicon_id, zap_tag )
		elif check_type == "lexiconmaxid":
			lexicon_maxid = int( check_value )
			self.process_multi( lexicon_maxid, zap_tag )
		elif check_type == "ddd":
			self.process_ddd()
		else:
			self.stdout.write( "unrecognized 1st parameter: %s\n" % check_type )

		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


	def process_single( self, lexicon_id, zap_tag ):
		self.stdout.write( "process_single: lexicon id: %d\n" % lexicon_id )

		ocr_docids = self.check_ocrdata( lexicon_id )
	#	self.loop_docs( docids )

		lexicon, metadata_count = self.check_metadata( lexicon_id )
		if lexicon == None:
			if  len( ocr_docids ) == 0:
				self.stdout.write( "Lexicon %d does not exist, and no OCR found\n" % lexicon_id )
				return False		# tag not zapped
			else:
				self.stdout.write( "Lexicon %d does no longer exist, but %d OCR docs remainded\n" % ( lexicon_id, len( ocr_docids ) ) )
				if zap_tag:
					self.ocr_striptag( lexicon_id, ocr_docids )
					return True			# tag not zapped
				else:
					return False		# tag not zapped


	def process_multi( self, lexicon_maxid, zap_tag ):
		self.stdout.write( "process_multi: lexicon max id: %d\n" % lexicon_maxid )

		for lexicon_id in range( lexicon_maxid ):
			self.stdout.write( "\nlexicon id: %d\n" % lexicon_id )
			zapped = self.process_single( lexicon_id, zap_tag )
			if zapped:
				self.stdout.write( "break after zapped lexicon id %d\n" % lexicon_id )
				break


	def check_ocrdata( self, lexicon_id ):
		tag = "Lexicon" + str( lexicon_id )
		self.stdout.write( "check_ocrdata: tag: %s\n" % tag )

		# get the doc ids by tag
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc"
		else:
			xtas_url = xtas_baseurl + "/doc"
	#	self.stdout.write( "xTAS url: %s\n" % xtas_url )

		params = { 'key' : settings.XTAS_API_KEY, 'tags' : tag }

		try:
			response = requests.get( xtas_url, params = params )
			content  = response.content
		except:
			self.stderr.write( "url: %s\n" % xtas_url )
			self.stderr.write( "params: %s\n" % params )
			type, value, tb = exc_info()
			self.stderr.write( "xTAS request failed: %s\n" % value.message )
			return

		jsdata = json.loads( response.content )
	#	print >> stderr, jsdata
		status = jsdata[ "status" ]
		if status == "error":
			docids = []
			ocrdata_count = 0
			if not ( jsdata[ "code" ] == 404 and jsdata[ "error" ] == "No documents found" ):
				print >> stderr, jsdata
		else:
			ocrdata_count = jsdata[ "result" ][ "count" ]
			docids = jsdata[ "result" ][ "ids" ]

		self.stderr.write( "found %s OCR documents for tag %s\n" % ( ocrdata_count, tag ) )
		return docids


	def check_metadata( self, lexicon_id ):
		self.stdout.write( "check_metadata: lexicon id: %d\n" % lexicon_id )

		try:
			lexicon = LexiconItem.objects.select_related().get( id = lexicon_id )
		except:
			type, value, tb = exc_info()
			if value.message == "<class 'BiLand.lexicon.models.DoesNotExist'>":
			#	self.stderr.write( "lexicon with id %d does not exist\n" % lexicon_id )
				pass
			else:
				self.stderr.write( "request failed: %s\n" % value.message )
			return None, 0

		metadata_count = lexicon.documents.count()
		self.stderr.write( "found %s metadata documents for lexicon id %d\n" % ( metadata_count, lexicon_id ) )

		return lexicon, metadata_count


	def loop_docs( self, docids ):
		count = len( docids )
		self.stdout.write( "loop_docs: count: %s\n" % count )

		error1_count = 0
		error2_count = 0
		keep_count   = 0
		delete_count = 0

		# loop docs to inspect tags
		for d in range( len( docids ) ):
			docid = docids[ d ]
			self.stderr.write( "# %d, docid: %s" % ( d, docid ) )
			# get document
			xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
			if len( settings.XTAS_PREFIX ) > 0:
				xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc"
			else:
				xtas_url = xtas_baseurl + "/doc"
		#	self.stdout.write( "xTAS url: %s\n" % xtas_url )

			params = { 'key' : settings.XTAS_API_KEY, 'id' : docid }

			try:
				response = requests.get( xtas_url, params = params )
				content  = response.content
			except:
				self.stderr.write( "url: %s\n" % xtas_url )
				self.stderr.write( "params: %s\n" % params )
				type, value, tb = exc_info()
				self.stderr.write( "xTAS request failed: %s\n" % value.message )
				error1_count += 1
				continue

			jsdata = json.loads( response.content )
		#	print >> stderr, jsdata
			status = jsdata[ "status" ]
			if status == "error":
				print >> stderr, jsdata
				error2_count += 1
				continue
			else:
				keep_count = 0
				delete_count = 0
				tags = jsdata[ "result" ][ "document" ][ "tags" ]
				if len( tags ) == 1 and tags[ 0 ] == KBtag:
					delete_count += 1
					self.stderr.write( " delete: %s\n" % tags )
				else:
					keep_count += 1
					self.stderr.write( " keep: %s\n" % tags )

		self.stderr.write( "error1_count: %d\n" % error1_count )
		self.stderr.write( "error2_count: %d\n" % error2_count )
		self.stderr.write( "delete_count: %d\n" % delete_count )
		self.stderr.write( "keep_count:   %d\n" % keep_count )


	def ocr_striptag( self, lexicon_id, ocr_docids ):
		tag = "Lexicon" + str( lexicon_id )
		self.stdout.write( "ocr_striptag: removing tag %s from %d documents\n" % ( tag, len( ocr_docids ) ) )

		path = "/doc/removetags"
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + path
		else:
			xtas_url = xtas_baseurl + path

		self.stdout.write( "xTas url: %s\n" % xtas_url )

		ids  = ",".join( ocr_docids )
		tags = tag
		delete = False		# True: delete doc if all tags matched
		params = { 'key' : settings.XTAS_API_KEY, 'ids' : ids, 'tags' : tags, 'delete' : delete }

		try:
			response = requests.post( xtas_url, data = params )
			content  = response.content
		except:
			self.stderr.write( "url: %s" % xtas_url )
			self.stderr.write( "params: %s" % params )
			type, value, tb = exc_info()
			self.stderr.write( "xTas request failed: %s" % value.message )
			article_count = 0

		if content == "200 Deleted\n":
			# response XML contains the list of docids that had the tag[s] removed, 
			# so that list may be shorter than the input list
			pass
		else:
			self.stderr.write( "params: %s\n" % params )
			self.stderr.write( "response: %s\n" % content )


	def process_ddd( self ):
		self.stdout.write( "process_ddd\n" )

		# get the doc ids by tag
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc"
		else:
			xtas_url = xtas_baseurl + "/doc"
	#	self.stdout.write( "xTAS url: %s\n" % xtas_url )

		params = { 'key' : settings.XTAS_API_KEY, 'tags' : KBtag }

		try:
			response = requests.get( xtas_url, params = params )
			content  = response.content
		except:
			self.stderr.write( "url: %s\n" % xtas_url )
			self.stderr.write( "params: %s\n" % params )
			type, value, tb = exc_info()
			self.stderr.write( "xTAS request failed: %s\n" % value.message )
			return

		jsdata = json.loads( response.content )
	#	print >> stderr, jsdata
		status = jsdata[ "status" ]
		if status == "error":
			docids = []
			if jsdata[ "code" ] == 404 and jsdata[ "error" ] == "No documents found":
				pass
			else:
				print >> stderr, jsdata
		else:
			ocrdata_count = jsdata[ "result" ][ "count" ]
			docids = jsdata[ "result" ][ "ids" ]
			self.stderr.write( "found %s OCR documents for tag %s\n" % ( ocrdata_count, KBtag ) )
			
# [eof]
