#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/management/commands/zaplexicondata.py
Version:	0.21
Goal:		1) Delete the metadata for the given lexicon
			2) Remove the lexicon tags from the lexicon articles
			Notice: the lexicon itself is not deleted, unless its name ends with "_daterange"
			execute in the $BILAND_HOME directory:
				$ ./manage.py zaplexicondata <type> <value>
					lexiconid   <lexicon_id>
					lexiconname <lexicon_name>
					username    <user_name>
			if the lexicon name consists of more than 1 word, enclose them in ""

FL-07-Dec-2011: Created
FL-10-Jan-2012: Bug in _daterange delete: only delete the lexicon, not the metadata!
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
		self.stdout.write( "zaplexicondata\n" )
		self.stdout.write( "%d args\n" % len( args ) )
		for arg in args:
			self.stdout.write( "arg: %s\n" % arg )

		lexicon_title = ''
		if len( args ) == 0:
			self.stdout.write( "no parameters specified\n" )
			return
		elif len( args ) == 1:
			self.stdout.write( "only one parameter specified, need two: <type> <value>\n" )
			return
		elif len( args ) > 2:
			self.stdout.write( "too many parameters specified, need two: <type> <value>\n" )
			return
		else:
			zap_type  =  args[ 0 ]
			zap_value =  args[ 1 ]
			self.stdout.write( "type: %s, value: %s\n" % ( zap_type, zap_value ) )

		types = [ "lexiconid", "lexiconname", "username" ]
		if zap_type == "lexiconid":
			lexicon_id = zap_value
			self.stdout.write( "lexicon id: %s\n" % lexicon_id )
			try:
				lexicons_qset = LexiconItem.objects.select_related().filter( id = lexicon_id )
			except:
				type, value, tb = exc_info()
				self.stderr.write( "request failed: %s" % value.message )
				return

		elif zap_type == "lexiconname":
			lexicon_title = zap_value
			self.stdout.write( "lexicon title: %s\n" % lexicon_title )
			lexicons_qset = LexiconItem.objects.select_related().filter( title = lexicon_title )

		elif zap_type == "username":
			lexicon_user = zap_value
			self.stdout.write( "lexicon user: %s\n" % lexicon_user )
			lexicons_qset = LexiconItem.objects.select_related().filter( user = lexicon_user )

		else:
			self.stdout.write( "wrong type, use one of: %s\n" % types )
			return

		nlexicons = lexicons_qset.count()		# instead of len(), when we do not need all hits to be retrieved
		self.stdout.write( "%d lexicons found\n" % nlexicons )


		for lexicon in lexicons_qset:
			if lexicon_title.endswith( "_daterange" ):
				# only delete the lexicon (and its crosstable links)
				lexicon.delete()
			else:
				# keep the lexicon, but delete its metadata & articles
				self.delete_metadata( lexicon )		# delete its metadata
				self.delete_docstag( lexicon )		# delete lexicon tag from documents

		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


	def delete_metadata( self, lexicon ):
		title      = lexicon.title
		created    = lexicon.created
		ndocuments = lexicon.documents.count()
		self.stdout.write( "delete_metadata: lexicon: %s\n" % title.encode( 'utf-8' ) )

		self.stdout.write( "lexicon '%s' was created on %s, containing %d metadata documents\n" % ( title.encode( 'utf-8' ), created, ndocuments ) )

		# bulk delete
	#	documents = lexicon.documents.delete()	# 'ManyRelatedManager' object has no attribute 'delete'

		# delete per document, when there is a custom delete() method on the model class
		documents = lexicon.documents.all()
		for document in documents:
			document.delete()


	def delete_docstag( self, lexicon ):
		lexicon_tag = "Lexicon" + str( lexicon.id )
		self.stdout.write( "delete_docstag: lexicon tag: %s\n" % lexicon_tag )

		# in order to delete the tag, we have to provide the list of docids as well
		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc"
		else:
			xtas_url = xtas_baseurl + "/doc"
		self.stdout.write( "xTAS url: %s\n" % xtas_url )

		params = { 'key' : settings.XTAS_API_KEY, 'tags' : lexicon_tag }

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
		print >> stderr, jsdata
		status = jsdata[ "status" ]
		if status == "error":
			print >> stderr, jsdata
			return
		else:
			ocrdata_count = jsdata[ "result" ][ "count" ]
			docids = jsdata[ "result" ][ "ids" ]
			self.stdout.write( "deleting tag from: %s\n" % docids )

		xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
		if len( settings.XTAS_PREFIX ) > 0:
			xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + "/doc/removetags"
		else:
			xtas_url = xtas_baseurl + "/doc/removetags"
		self.stdout.write( "xTAS url: %s\n" % xtas_url )

		params = { 'key' : settings.XTAS_API_KEY, 'ids' : ','.join( docids ), 'tags' : lexicon_tag }
	#	self.stdout.write( "params: %s\n" % params )

		try:
			response = requests.get( xtas_url, params = params )
		except:
			self.stderr.write( "url: %s" % xtas_url )
			self.stderr.write( "params: %s" % params )
			type, value, tb = exc_info()
			self.stderr.write( "xTAS request failed: %s" % value.message )

		jsdata = json.loads( response.content )
		status = jsdata[ "status" ]
		if status == "error":
			print >> stderr, jsdata

# [eof]
