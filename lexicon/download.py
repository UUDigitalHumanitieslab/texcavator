# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Copyright:	Daan Odijk, Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BILAND
Name:		lexicon/download.py
Version:	0.22
Goal:		create zipfile with queru ocr+meta-data
To do:		remove expired zipfiles with the command `at'
			delegate the zipping to celery

def request2extra4log( request )
def create_zipname( username, query_title 
def download_prepare( request )
def download_collect( req_dict, zip_basename, to_email, email_message )
def zip_chunk( ichunk, hits_list, zip_file, csv_writer, format )
def hit2csv_header( csv_writer, ichunk, hit )
def hit2csv_data( csv_writer, hit, es_header_names, kb_header_names )
def get_es_chunk( es_query_str, start_record, chunk_size )
def clean_filename( s )
def download_data( request, zip_basename )
def execute( merge_dict, zip_basename, to_email, email_message )
def expire_data()

FL-04-Jun-2013: Created
FL-19-Dec-2013: Changed
"""

import os
from sys import stderr, exc_info
import csv
import requests
import collections
from time import ctime, localtime, strftime, time
import datetime
import unicodedata
import string
from urllib import quote_plus, urlencode
import zipfile
from dicttoxml import dicttoxml

import base64
import subprocess

import logging
logger = logging.getLogger( __name__ )

import json

from django.contrib import auth
from django.conf import settings
from django.core.mail import send_mail
from django.core.servers.basehttp import FileWrapper
from django.core.validators import email_re
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from services.cql2es import cql2es_error, callperl
from services.request import request2article_types, request2article_distrib, request2parms
from BILAND.views import get_ext_server_info


def request2extra4log( request ):
	# pop conflicting keys
#	extra = request.META
#	extra.pop( "module", None )			# "Attempt to overwrite 'module' in LogRecord"
	# do we need to pop more?

	# minimum variant, can't do without 'REMOTE_ADDR' key
	try:
		remote_addr = request.META[ 'REMOTE_ADDR' ]
	except:
		remote_addr = ""
	extra = { 'REMOTE_ADDR' : remote_addr }
	return extra



def create_zipname( username, query_title ):
	query_title_ = username + '_' + query_title
	query_title_ = clean_filename( query_title_ )
	zip_basename = query_title_ + "_" + strftime( "%Y.%m.%d-%H.%M.%S" )

	return zip_basename



@csrf_exempt
def download_prepare( request ):
	"""
	Request from BiLand to create the ocr+meta-data zipfile for download
	"""
	extra = request2extra4log( request )

	msg =  "%s: %s" % ( __name__, "download_prepare()" )
	logger.debug( msg, extra = extra )
	if settings.DEBUG == True: 
		print >> stderr, "download_prepare()"
		print >> stderr, request.REQUEST

	req_dict = request.REQUEST

	try:
		username    = req_dict[ 'username' ]
		password    = req_dict[ 'password' ]
		query_title = req_dict[ 'query_title' ]
	except( KeyError ):
		msg = "key error on 'username', 'password', 'query_title', 'query', or 'dateRange'"
		if settings.DEBUG == True:
			print >> stderr, msg
		logger.warn( msg, extra = extra )
		resp_dict = { 'status' : 'error', 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	query_str, literal, date_begin, date_end, start_record, chunk_size, collection = request2parms( request.REQUEST )

	if query_title == "" or query_str == "":
		msg = "empty query title or content"
		if settings.DEBUG == True:
			print >> stderr, msg
			print >> stderr, request.META
		logger.warn( msg, extra = extra )
		resp_dict = { 'status' : "error", 'msg' : msg }
		return HttpResponse( json.dumps( resp_dict ) )

	user = auth.authenticate( username = username, password = password )
	if user is None:
		if settings.DEBUG == True:
			print >> stderr, "user:", "None"
		msg = "unrecognized user: %s" % username
		logger.warn( msg, extra = extra )
		resp_dict = { 'status' : "error", 'msg' : msg }
		return HttpResponse( json.dumps( resp_dict ) )

	# Add the date range
	query_str += " AND (paper_dc_date >= " + date_begin + " AND paper_dc_date <= " + date_end + ")"

	# Add the KB document type[s] selection to the query
	doc_types = request2article_types( request.REQUEST )
	if settings.DEBUG == True:
		print >> stderr, "type_query:", doc_types, collection
	if collection == settings.ES_INDEX_KONBIB and doc_types is not None:
		query_str += doc_types

	# Add the KB document distribution[s] selection to the query
	distrib_types = request2article_distrib( request.REQUEST )
	if settings.DEBUG == True:
		if not distrib_types:
			print >> stderr, "distrib_query:", "None", collection
		else:
			print >> stderr, "distrib_query:", distrib_types.encode( "utf-8" ), collection
	if collection == settings.ES_INDEX_KONBIB and distrib_types is not None:
		query_str += distrib_types

	print >> stderr, query_str.encode( "utf-8" )

	# check query conversion
#	try:
#		literal = req_dict[ 'literal' ]
#	except:
#		literal = False

	try:
		es_query_str = callperl( query_str, literal )	# call Perl: CQL -> ES JSON
	except:
		type, value, tb = exc_info()
		return cql2es_error( value )

	print >> stderr, "es_query_str:", es_query_str

	if user.email == "":
		msg = "Preparing your download for query <br/><b>" + query_title + "</b> failed.<br/>A valid email address is needed for user <br/><b>" + user.username + "</b>"
		if settings.DEBUG == True: print >> stderr, msg
		logger.warn( msg, extra = extra )
		resp_dict = { 'status' : 'error', 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	if not email_re.match( user.email ):
		msg = "Preparing your download for query <br/><b>" + query_title + "</b> failed.<br/>The email address of user <b>" + user.username +  "</b> could not be validated: <b>" + to_email + "</b>"
		if settings.DEBUG == True: print >> stderr, msg
		logger.warn( msg, extra = extra )
		resp_dict = { 'status' : 'error', 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	zip_basename = create_zipname( username, query_title )			# proper basename, with username and timestamp
	scheme_authority, sub_site = get_ext_server_info( request )
	url = os.path.join( scheme_authority + sub_site + "lexicon/download/data/" + quote_plus( zip_basename ) )
	email_message = "BiLand Query: " + query_title + "\n" + zip_basename + \
		"\nURL: " + url

#	download_collect( req_dict, zip_basename )						# zip documents
#	task_download_collect( req_dict, zip_basename )					# zip documents by celery
	execute( req_dict, zip_basename, user.email, email_message )	# zip documents by management cmd

	msg = "Your download for query <b>" + query_title + "</b> is being prepared.<br/>When ready, an email will be sent to <b>" + user.email + "</b>"
	resp_dict = { 'status' : 'SUCCESS', 'msg' : msg }
	json_list = json.dumps( resp_dict )
	ctype = 'application/json; charset=UTF-8'
	return HttpResponse( json_list, content_type = ctype )



def download_collect( req_dict, zip_basename, to_email, email_message ):
	"""
	Actual creation/collection of document files
	"""
	extra = { 'REMOTE_ADDR' : "" }

	msg =  "%s: %s" % ( __name__, "download_collect()" )
	logger.debug( msg, extra = extra )
	if settings.DEBUG == True: print >> stderr, msg

	query_str, literal, date_begin, date_end, start_record, chunk_size, collection = request2parms( req_dict )

	# download format: JSON or XML
	try:
		format = req_dict[ "format" ]
	except:
		format = "json"
	if settings.DEBUG == True: print >> stderr, "format", format

	# Add the date range
	query_str += " AND (paper_dc_date >= " + date_begin + " AND paper_dc_date <= " + date_end + ")"

	# Add the KB document type[s] selection to the query
	doc_types = request2article_types( req_dict )
	if settings.DEBUG == True: print >> stderr, "type_query", doc_types
	if collection == settings.ES_INDEX_KONBIB and doc_types is not None:
		query_str += doc_types

	# Add the KB document distribution[s] selection to the query
	distrib_types = request2article_distrib( req_dict )
	if settings.DEBUG == True:
		if not distrib_types:
			print >> stderr, "distrib_query:", "None", collection
		else:
			print >> stderr, "distrib_query:", distrib_types.encode( "utf-8" ), collection
	if collection == settings.ES_INDEX_KONBIB and distrib_types is not None:
		query_str += distrib_types

	print >> stderr, query_str.encode( "utf-8" )

	try:
		es_query_str = callperl( query_str, literal )	# call Perl: CQL -> ES JSON
	except:
		type, value, tb = exc_info()
		return cql2es_error( value )

	msg = "es_query: %s" % es_query_str
	logger.debug( msg, extra = extra )
	if settings.DEBUG == True: print >> stderr, msg

	# just get the hit count
	start_record = 0
	chunk_1_size = 1
	hits, resp_object = get_es_chunk( es_query_str, start_record, chunk_1_size )

	if resp_object is not None:
		return resp_object

	zip_basedir  = settings.QUERY_DATA_DOWNLOAD_PATH
	zip_filename = zip_basename + ".zip"
	zip_pathname = os.path.join( zip_basedir, zip_filename )

	logger.debug( zip_pathname, extra = extra )
	if settings.DEBUG == True: print >> stderr, zip_pathname

	# create zipfile
	try:
		zip_file = zipfile.ZipFile( zip_pathname, mode = 'w', compression = zipfile.ZIP_DEFLATED )
	except:
		type, value, tb = exc_info()
		msg = "opening OCR file failed: %s" % value
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = { "status" : "error", "msg" : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	# how many chunks do we need?
	from math import ceil
	chunk_size = settings.QUERY_DATA_CHUNK_SIZE
	hits_total = hits[ "total" ]
	nchunks = int( ceil( float( hits_total ) / float( chunk_size ) ) )
	hits_zipped = 0

	csv_writer = None
	if format == "csv":
		csv_filename = zip_basename + ".csv"
		csv_pathname = os.path.join( zip_basedir, csv_filename )
		# create csv file
		try:
			csv_file = open( csv_pathname, 'w')
			quotechar = '"'		# default
		#	quotechar = '|'
			csv_writer = csv.writer( csv_file, delimiter = '\t', quoting = csv.QUOTE_NONNUMERIC, quotechar = quotechar )
		except:
			type, value, tb = exc_info()
			msg = "opening CSV file failed: %s" % value
			if settings.DEBUG == True: print >> stderr, msg
			resp_dict = { "status" : "error", "msg" : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )

	for ichunk in range( nchunks ):
		start_record = ichunk * chunk_size
		nchunk = ichunk + 1

		if settings.DEBUG == True:
			print >> stderr, "nchunk:", nchunk, "of", nchunks, "start_record:", start_record

		hits, resp_object = get_es_chunk( es_query_str, start_record, chunk_size )

		hits_list = hits[ "hits" ]
		hits_zipped += len( hits_list )
		zip_chunk( ichunk, hits_list, zip_file, csv_writer, format )

	if format == "csv":
		csv_file.close()
		csv_file = open( csv_pathname, 'r')
		zip_file.writestr( csv_filename, csv_file.read() )
		csv_file.close()
		if settings.DEBUG == True:
			print >> stderr, "deleting %s" % csv_pathname
		os.remove( csv_pathname ) 	# not needed anymore

	if settings.DEBUG == True:
		print >> stderr, "hits_zipped:", hits_zipped

	# send email
	from_email = "a.c.laan@uva.nl"
	to_email   = to_email
	subject    = "BiLand data download"
	msg = "sending email to %s" % to_email
	logger.debug( msg, extra = extra )
	if settings.DEBUG == True: print >> stderr, msg
	send_mail( subject, email_message, from_email, [ to_email ], fail_silently = False )



def zip_chunk( ichunk, hits_list, zip_file, csv_writer, format ):
	extra = { 'REMOTE_ADDR' : "" }

	msg =  "%s: %s" % ( __name__, "zip_chunk()" )
	logger.debug( msg, extra = extra )
	if settings.DEBUG == True: print >> stderr, msg

	if hits_list is None:
		print >> stderr, "zip_chunk(): empty hit list"
		return

	for h in range( len( hits_list ) ):
		hit = hits_list[ h ]

	#	_index  = hit[ "_index" ]
	#	_type   = hit[ "_type" ]
		_id     = hit[ "_id" ]

	#	if settings.DEBUG == True:
		#	print >> stderr, "_id:", _id
		#	print >> stderr, "hit:", hit

		pseudo_filename = _id.replace( ':', '-' )		# use '-' instead of ':' in file names
		if format == "xml":
			pseudo_filename += ".xml"
			xml = dicttoxml( hit )
		#	if settings.DEBUG == True: print >> stderr, xml.encode( "utf-8" )
			zip_file.writestr( pseudo_filename, xml.encode( "utf-8" ) )
		elif format == "csv":
			if h == 0:
				es_header_names, kb_header_names = hit2csv_header( csv_writer, ichunk, hit )
			hit2csv_data( csv_writer, hit, es_header_names, kb_header_names )
		else: 		# "json"
			pseudo_filename += ".json"
			zip_file.writestr( pseudo_filename, json.dumps( hit ) )


def hit2csv_header( csv_writer, ichunk, hit ):
#	if settings.DEBUG == True: print >> stderr, "hit2csv_header()"
#	if settings.DEBUG == True: print >> stderr, hit

	es_header_names = \
	[
		"_id",								#  0
		"_score"							#  1
	]
 
	kb_header_names = \
	[
		"identifier",						#  2

		"paper_dc_date",					#  3
		"paper_dc_identifier",				#  4
 		"paper_dc_identifier_resolver",		#  5
		"paper_dc_language",				#  6
		"paper_dc_title",					#  7
		"paper_dc_publisher",				#  8
		"paper_dc_source",					#  9

		"paper_dcterms_alternative", 		# 10
		"paper_dcterms_isPartOf",			# 11
		"paper_dcterms_isVersionOf",		# 12
		"paper_dcterms_issued",				# 13
		"paper_dcterms_spatial",			# 14
		"paper_dcterms_spatial_creation", 	# 15
 		"paper_dcterms_temporal",			# 16

		"paper_dcx_issuenumber",			# 17	sometimes contains '-' instead of a number
		"paper_dcx_recordRights",  			# 18
		"paper_dcx_recordIdentifier", 		# 19
  		"paper_dcx_volume",					# 20

		"paper_ddd_yearsDigitized",			# 21

		"article_dc_identifier_resolver",	# 21
		"article_dc_subject",				# 22
		"article_dc_title",					# 23
		"article_dcterms_accessRights",		# 24
		"article_dcx_recordIdentifier",		# 25

		"text_content"						# 26
	]

	header_names = es_header_names + kb_header_names

	if ichunk == 0:
		csv_writer.writerow( header_names )

	return es_header_names, kb_header_names



def hit2csv_data( csv_writer, hit, es_header_names, kb_header_names ):
#	if settings.DEBUG == True: print >> stderr, "hit2csv_data()"
#	if settings.DEBUG == True: print >> stderr, hit

	es_line = []
	for es_name in es_header_names:
		try:
			val = hit[ es_name ]
		except:
			val = ""
		es_line.append( val )

	kb_line = []
	_source = hit[ "_source" ]
	for kb_name in kb_header_names:
		try:
			if _source[ kb_name ] == '-':	# in number fields, this troubles Jose's SPSS
				val = ''
			else:
				val = _source[ kb_name ].encode( "utf-8" )

		#	if kb_name == "text_content":
		#		val.replace( '\r', '|' )
		#		val.replace( '\n', '|' )
		except:
			val = ""
		kb_line.append( val )

	data_line = es_line + kb_line

	csv_writer.writerow( data_line )



def get_es_chunk( es_query_str, start_record, chunk_size ):
	extra = { 'REMOTE_ADDR' : "" }

	msg =  "%s: %s" % ( __name__, "get_es_chunk(" )
	logger.debug( msg, extra = extra )
	if settings.DEBUG == True: print >> stderr, msg

	hits_list = None

	# limit the response fields to what we need; prefix "_source." is superfluous
	fields = \
	[
		"article_dc_title",
		"paper_dcterms_temporal",
		"paper_dcterms_spatial",
		"paper_dc_title",
		"paper_dc_date"
	]

	params = \
	{
		"from"   : start_record,		# ES start record: default =  0 (KB default = 1)
		"size"   : chunk_size,			# ES default chunk count = 10, Biland assumes 20
	#	"fields" : ",".join( fields ),	# supply as a string	# SKIPPING fields filter
		"source" : es_query_str
	}

	es_baseurl = "http://" + settings.ELASTICSEARCH_HOST + ':' + str( settings.ELASTICSEARCH_PORT ) + '/'
	es_url = es_baseurl + settings.ES_INDEX_KONBIB
	es_url += "/_search/"

	try:
		response = requests.get( es_url, params = params )
	except:
		if settings.DEBUG == True:
			print >> stderr, "url: %s" % es_url
			print >> stderr, "params: %s" % params

		type, value, tb = exc_info()
		msg = "ElasticSearch request failed: %s" % value
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = { "status" : "error", "msg" : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return hits_list, HttpResponse( json_list, content_type = ctype )

	es_dict = json.loads( response.content )

#	if settings.DEBUG == True: print >> stderr, es_dict

	took      = es_dict[ "took" ]
	timed_out = es_dict[ "timed_out" ]
	_shards   = es_dict[ "_shards" ]
	hits      = es_dict[ "hits" ]

	_shards_total      = _shards[ "total" ]
	_shards_successful = _shards[ "successful" ]
	_shards_failed     = _shards[ "failed" ]

	hits_total     = hits[ "total" ]
#	hits_max_score = hits[ "max_score" ]
	hits_list      = hits[ "hits" ]

	if settings.DEBUG == True:
		print >> stderr, "took: %d" % took
		print >> stderr, "timed_out: %s" % timed_out

		print >> stderr, "_shards_total: %d" % _shards_total
		print >> stderr, "_shards_successful: %d" % _shards_successful
		print >> stderr, "_shards_failed: %d" % _shards_failed

		print >> stderr, "hits_total: %d" % hits_total
		print >> stderr, "hits_list: %d" % len( hits_list )

	return hits, None



def clean_filename( s ):
	# strip problematic characters from filename

	s = ''.join( ( c for c in unicodedata.normalize( 'NFD', s ) if unicodedata.category( c ) != 'Mn' ) )
	s = s.replace( ' ', '_' )
	s = "".join( i for i in s if (i.isalnum() or i=='_') )
	return s



@csrf_exempt
def download_data( request, zip_basename ):
	"""
	This request occurs when the user clicks the download link that we emailed
	"""
	extra = { 'REMOTE_ADDR' : "" }

	msg = "download_data() zip_basename: %s" % zip_basename
	logger.debug( msg, extra = extra )
	if settings.DEBUG == True: print >> stderr, msg
	# to do: use mod_xsendfile

	zip_basedir  = os.path.join( settings.PROJECT_PARENT, settings.QUERY_DATA_DOWNLOAD_PATH )
	zip_filename = zip_basename + ".zip"
	zip_pathname = os.path.join( zip_basedir, zip_filename )

	wrapper = FileWrapper( open( zip_pathname, 'r' ) )
	response = HttpResponse( wrapper, content_type='application/zip' )
	response[ 'Content-Length' ] = os.path.getsize( zip_pathname )
	response[ 'Content-Disposition' ] = "attachment; filename=%s" % zip_filename

	return response



def execute( merge_dict, zip_basename, to_email, email_message ):
	if settings.DEBUG:
		print >> stderr, "execute()"
	logger.debug( "%s: %s" % ( __name__, "execute()" ) )

	#	print >> stderr, merge_dict.items()
	#	print >> stderr, merge_dict.keys()
	#	print >> stderr, merge_dict.values()

	if settings.QUERY_DATA_DELETE_DATA:
		expire_data()		# delete old download stuff

	keys   = merge_dict.keys()
	values = merge_dict.values()
	req_dict = {}
	for i in range( len( keys ) ):
		req_dict[ keys[ i ] ] = values[ i ]

	# add the zip name & user email
	req_dict[ "zip_basename" ]  = zip_basename
	req_dict[ "to_email" ]      = to_email
	req_dict[ "email_message" ] = email_message
	if settings.DEBUG:
		print >> stderr, req_dict
		print type( req_dict )

	req_str = json.dumps( req_dict )
	req_base64 = base64.b64encode( req_str )
	if settings.DEBUG:
		print >> stderr, req_base64

	vpython = settings.QUERY_DATA_VPYTHON_PATH + "/bin/activate"
	program = os.path.join( settings.PROJECT_PARENT, "manage.py" )

#	class subprocess.Popen(args, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, 
#		preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, 
#		universal_newlines=False, startupinfo=None, creationflags=0)

	if settings.QUERY_DATA_DOWNLOAD_DETACH:		# we do not want to wait: close_fds = True
		# need to set proper environment
		cmdline  = "source " + vpython + "; "
		cmdline += 'python ' + program + ' zipquerydata "' + req_base64 + '"'
		if settings.DEBUG:
			print cmdline, "\n"

		p = subprocess.Popen( cmdline, shell = True, close_fds = True )
		resp_str = ""
	else:						# this cmd waits until completion, defaul: close_fds = False
		cmdline += 'python ' + program + ' zipquerydata "' + req_base64 + '"'
		if settings.DEBUG:
			print cmdline, "\n"

		p = subprocess.Popen( cmdline, shell = True, stdout = subprocess.PIPE )
		resp_str = p.stdout.read()
		if settings.DEBUG:
			print >> stderr, "resp_str: |%s|" % resp_str

	return resp_str



def expire_data():
	extra = { 'REMOTE_ADDR' : "" }

	msg = "%s: %s" % ( __name__, "expire_data()" )
	logger.debug( msg, extra = extra )
	if settings.DEBUG: print >> stderr, "expire_data()"

	ddir = settings.QUERY_DATA_DOWNLOAD_PATH
	if settings.DEBUG:
		print >> stderr, "download path:", ddir

#	expire_after = 
	time_now = datetime.datetime.now()		# <type 'datetime.datetime'>
	if settings.DEBUG:
		print >> stderr, "time_now:", time_now

	files = os.listdir( ddir )
	files.sort()
	for fname in files:
		if settings.DEBUG:
			print >> stderr, fname
		fpath = os.path.join( ddir, fname )
		if settings.DEBUG:
			print >> stderr, fpath

		time_created_float = os.path.getctime( fpath )
		time_created = datetime.datetime.fromtimestamp( time_created_float )	# <type 'datetime.datetime'>
		if settings.DEBUG:
			print>> stderr, "time_created: %s" % time_created

		# elapsed time as <type 'datetime.timedelta'>;  days, seconds and microseconds are stored internally
		elapsed = time_now - time_created
		if settings.DEBUG:
			print>> stderr, "elapsed: %s" % elapsed

	#	print "elapsed days:   %s" % elapsed.days
	#	print "elapsed seconds: %s" % elapsed.seconds
	#	print "elapsed microseconds: %s" % elapsed.microseconds

		if elapsed.days >= settings.QUERY_DATA_EXPIRE_DAYS:
			msg = "deleting query data file: %s" % fpath
			logger.debug( msg, extra = extra )
			if settings.DEBUG: print>> stderr, msg

			try:
				os.remove( fpath ) 		# DELETING QUERY DATA DOWNLOAD FILE
			except:
				type, value, tb = exc_info()
				msg = "deleting qyery data file failed: %s" % value
				logger.debug( msg, extra = extra )
				if settings.DEBUG == True: print >> stderr, msg

		else:
			msg = "keeping query data file: %s" % fpath
			logger.debug( msg, extra = extra )
			if settings.DEBUG: print>> stderr, msg


# [eof]
