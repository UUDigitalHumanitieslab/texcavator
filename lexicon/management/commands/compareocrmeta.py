#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/compareocrmeta.py
Version:	0.1
Goal:		Compare the existance of OCR & Metadata for a query
			execute in the $BILAND_HOME directory:
				$ ./manage.py compareocrmeta  <query_name>
			if the lexicon name consists of more than 1 word, enclose them in ""

FL-15-Nov-2012: Created
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


class Command( BaseCommand ):
	def handle( self, *args, **kwargs ):
		t1 = time()
		self.stdout.write( "compareocrmeta\n" )
		self.stdout.write( "%d args\n" % len( args ) )
		for arg in args:
			self.stdout.write( "arg: %s\n" % arg )

		lexicon_title = ''
		repair = False
		if len( args ) == 0:
			self.stdout.write( "no lexicon name specified\n" )
			return
		if len( args ) >= 1:
			lexicon_title = args[ 0 ]
			self.stdout.write( "lexicon_title: %s\n" % lexicon_title )
		if len( args ) >= 2:
			if args[ 1 ] == "repair":
				repair = True
		self.stdout.write( "repair: %s\n" % repair )

		lexicons_qset = LexiconItem.objects.select_related().filter( title = lexicon_title )
		nlexicons = lexicons_qset.count()		# instead of len(), when we do not need all hits to be retrieved
		if nlexicons == 0:
			self.stdout.write( "lexicon with title '%s' was not found\n" % lexicon_title )
		elif nlexicons > 1:
			self.stdout.write( "%d lexicons with title %s !\n" % ( nlexicons, lexicon_title ) )
			for lexicon in lexicons_qset:
				self.stdout.write( "user: %s\n" % lexicon.user )
			return

		for lexicon_qset in lexicons_qset:
			if lexicon_title.endswith( "_daterange" ):
				self.stdout.write( "ignoring query '%s'\n" % lexicon_title )
			else:
				self.stdout.write( "checking query '%s'\n" % lexicon_title )
				lexicon_id, metadata_ids = self.get_metadata( lexicon_title )
				ocrdata_ids = self.get_ocrdata_ids( lexicon_id, lexicon_title )
				nomatch_meta, nomatch_ocr = self.compare_ocr_meta( metadata_ids, ocrdata_ids, repair )

				if repair:
					lexicon_tag = "Lexicon" + str( lexicon_id )
					self.repair_metadata( lexicon_tag, nomatch_meta )
					self.repair_ocrdata(  lexicon_tag, nomatch_ocr )


		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


	def get_metadata( self, lexicon_title ):
		# get metadata from django
		try:
			lexicon = LexiconItem.objects.get( title = lexicon_title )
			lexicon_id = lexicon.id
			self.stdout.write( "Query id: %d\n" % lexicon_id )
			lexicon_title = lexicon.title
			metadata_count = lexicon.documents.count()
		except:
			lexicon_title = ''
			metadata_count = 0
			type, value, tb = exc_info()
			if value.message == "<class 'lexicon.models.DoesNotExist'>":
				pass	# no lexicon data for this lexicon_id
			else:
				self.stdout.write( "django request failed: %s\n" % value.message )

		nums_meta = []
		metadata_ids = []
		if metadata_count > 0:
			articles = lexicon.documents.all()
			for m in range( metadata_count ):
				article = articles[ m ]
				metadata_ids.append( article.identifier )
				nums_meta.append( m+1 )

		self.stdout.write( "metadatas: %d\n" % len( metadata_ids ) )
		metadata_ids.sort()

		return lexicon_id, metadata_ids


	def get_ocrdata_ids( self, lexicon_id, lexicon_title ):
		# get OCR data from xTas
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc"
		else:
			xtas_url = xtas_baseurl + "/doc"
	#	self.stdout.write( "url: %s\n" % xtas_url )

		lexicon_tag = "Lexicon" + str( lexicon_id )
		params = { 'key' : settings.XTAS_API_KEY, 'tags' : lexicon_tag }

		try:
			response = requests.get( xtas_url, params = params )
		except:
			self.stdout.write( "url: %s\n" % xtas_url )
			self.stdout.write( "params: %s\n" % params )
			type, value, tb = exc_info()
			self.stdout.write( "xTas request failed: %s\n" % value.message )
			ocrdata_count = 0
			ids = []
			return ids

		content = response.content
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

		ids = []
		if ocrdata_count > 0:
			ids = jsdata[ "result" ][ "ids" ]
			ids.sort()
		return ids



	def compare_ocr_meta( self, metadata_ids, ocrdata_ids, repair ):
		try:
			from heapq import merge			# python 2.6+
			docs = list( merge( metadata_ids, ocrdata_ids ) )
		except:
		#	type, value, tb = exc_info()
		#	self.stdout.write( "%s\n" % value.message )
			docs = sorted( metadata_ids + ocrdata_ids )

		docs = list( set( docs ) )			# remove duplicates
		num_docs = len( docs )
		self.stdout.write( "merged: %d\n" % int( num_docs ) )

		# mark in which list(s) the doc are
		nums = []
		in_meta = []
		in_ocrs = []

		for d in range( num_docs ):
			doc = docs[ d ]
		#	self.stdout.write( "%s\n" % doc )
			nums.append( d+1 )

			try:
				metadata_ids.index( doc )
				meta = True
			except:
				meta = False
			in_meta.append( meta )

			try:
				ocrdata_ids.index( doc )
				ocr = True
			except:
				ocr = False
			in_ocrs.append( ocr )

		match = 0
		nomatch = 0
		nomatch_meta = []
		nomatch_ocr = []
		for d in range( num_docs ):
			doc = docs[ d ]
			meta = in_meta[ d ]
			ocr  = in_ocrs[ d ]
			if meta == False or ocr == False:
				nomatch += 1
				self.stdout.write( "%s: Meta: %s, OCR: %s\n" % ( doc, meta, ocr ) )
				if meta == False:
					nomatch_meta.append( doc )
				if ocr == False:
					nomatch_ocr.append( doc )

			else:
				match += 1
			#	self.stdout.write( "%s: Meta: %s, OCR: %s\n" % ( doc, meta, ocr ) )

		self.stdout.write( "total: %d, match: %d, nomatch: %d\n" % ( num_docs, match, nomatch ) )

		# sometimes the merged length is smaller than either metadata_ids or ocrdata_ids length ?
		# explicit comparison of the 2 lists: 
		meta_in_ocr  = 0
		meta_out_ocr = 0
		for i in range( len( metadata_ids ) ):
			meta = metadata_ids[ i ]
			try:
				ocrdata_ids.index( meta )
				meta_in_ocr += 1
			except:
			#	self.stdout.write( "%d metadata id %s not in ocrdata list\n" % ( i, meta ) )
				meta_out_ocr += 1
		self.stdout.write( "meta_in_ocr: %d, meta_out_ocr: %d\n" % ( meta_in_ocr, meta_out_ocr ) )
	#	self.stdout.write( "\n" )

		ocr_in_meta  = 0
		ocr_out_meta = 0
		for i in range( len( ocrdata_ids ) ):
			ocr = ocrdata_ids[ i ]
			try:
				metadata_ids.index( ocr )
				ocr_in_meta += 1
			except:
			#	self.stdout.write( "%d ocrdata id %s not in metadata list\n" % ( i, ocr ) )
				ocr_out_meta += 1
		self.stdout.write( "ocr_in_meta: %d, ocr_out_meta: %d\n" % ( ocr_in_meta, ocr_out_meta ) )
	#	self.stdout.write( "\n" )

		return nomatch_meta, nomatch_ocr


	def fetch_document_ocr( self, doc_id ):
		# get OCR data from xTas
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc"
		else:
			xtas_url = xtas_baseurl + "/doc"
	#	self.stdout.write( "url: %s\n" % xtas_url )

		params = { 'key' : settings.XTAS_API_KEY, 'id' : doc_id }

		try:
			response = requests.get( xtas_url, params = params )
		except:
			self.stdout.write( "url: %s\n" % xtas_url )
			self.stdout.write( "params: %s\n" % params )
			type, value, tb = exc_info()
			self.stdout.write( "xTas request failed: %s\n" % value.message )
			ocrdata_count = 0

		content = response.content
		jsdata = json.loads( response.content )
		status = jsdata[ "status" ]
	#	print >> stderr, "content:", content

		if status == "error":
			code = jsdata[ "code" ]			# code = 404
			error = jsdata[ "error" ]		# Document not found"
			document = ""
			tags = ""
		#	self.stdout.write( "error: %s\n" % error )
		elif status == "ok":
			code = ""
			error = ""
			document = jsdata[ "result" ][ "document" ]
			tags = document[ "tags" ]
		#	self.stdout.write( "document: %s\n" % document )
		#	self.stdout.write( "tags: %s\n" % tags )
		else:
			code = ""
			error = ""
			document = ""
			tags = ""
			pass

		return status, code, error, document, tags


	def add_tag_to_document( self, doc_id, tag ):
		# add a [lexicon]tag to an existing document
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc/addtags"
		else:
			xtas_url = xtas_baseurl + "/doc/addtags"
	#	self.stdout.write( "url: %s\n" % xtas_url )

		params = { 'key' : settings.XTAS_API_KEY, 'ids' : doc_id, 'tags' : tag }

		try:
			response = requests.get( xtas_url, params = params )
		except:
			self.stdout.write( "url: %s\n" % xtas_url )
			self.stdout.write( "params: %s\n" % params )
			type, value, tb = exc_info()
			self.stdout.write( "xTas request failed: %s\n" % value.message )
			ocrdata_count = 0

		content = response.content
		jsdata = json.loads( response.content )
		status = jsdata[ "status" ]
	#	print >> stderr, "content:", content
		return status


	def repair_ocrdata( self, lexicon_tag, nomatch_ocr, ):
		if len( nomatch_ocr ) > 0:
			self.stdout.write( "repairing ocrdata...\n" )
			for doc_id in nomatch_ocr:
				self.stdout.write( "%s" % doc_id )

				# try to fetch documents
				status, code, error, document, tags = self.fetch_document_ocr( doc_id )
				if status == "ok":							# document present, check tags
				#	self.stdout.write( "tags: %s\n" % tags )
					try:
						tags.index( lexicon_tag )
						# found; nothing to do
					except:
						# not found; add tag
						status = self.add_tag_to_document( doc_id, lexicon_tag )
						self.stdout.write( " status: %s\n" % status )

				elif status == "error" and code == 404:		# document not present
					self.stdout.write( "retrieving: %s\n" % doc_id )
					self.stdout.write( "UNFINISHED..." )

	def repair_metadata( self, lexicon_tag, nomatch_meta ):
		if len( nomatch_meta ) > 0:
			self.stdout.write( "repairing metadata...\n" )
			for doc_id in nomatch_meta:
				self.stdout.write( "%s\n" % doc_id )
				self.stdout.write( "UNFINISHED..." )


# [eof]
