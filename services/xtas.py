# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		xtas.py
Version:	0.2
Goal:		ElasticSearch functions

def xtas_add_tags( doc_ids, tags ):
def addtags_elasticsearch( lexiconID, begindate, enddate )

FL-13-Feb-2013: Created
FL-10-Sep-2013: Changed
"""

import os
from sys import stderr, exc_info
import requests
import json

from django.conf import settings


def xtas_add_tags( doc_ids, tags ):
	path = "/doc/addtags"
	xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )
	if len( settings.XTAS_PREFIX ) > 0:
		xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX + path
	else:
		xtas_url = xtas_baseurl + path

	params = \
	{
		"key" : settings.XTAS_API_KEY,
		"ids"  : doc_ids,
		"tags" : tags
	}

	if settings.DEBUG == True:
		print >> stderr, "xTAS url: %s\n" % xtas_url
		print >> stderr, "params: %s\n" % params

	try:
		response = requests.get( xtas_url, params = params )
		content  = json.loads( response.content )
	except:
		if settings.DEBUG == True:
			print >> stderr, "xTAS url: %s\n" % xtas_url
			print >> stderr, "params: %s" % params

		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "xTAS request failed: %s" % value.message

		content = \
		{
			"status" : "exception",
			"error"  : value.message
		}

	if settings.DEBUG == True:
		print >> stderr, content

	return content



def addtags_elasticsearch( lexiconID, collection, begindate, enddate ):
	"""\
	Add the lexicon tag to the lexicon documents. 
	Get the query string from the Django db. 
	Get the document ids from ElasticSearch for the given date range. 
	Let xTAS add the tag to the documents. 
	"""
	if settings.DEBUG == True:
		print >> stderr, "addtags_elasticsearch()"

	# get the query string from the Django db
	try:
		li = LexiconItem.objects.get( pk = lexiconID )
	except LexiconItem.DoesNotExist:
		msg = "Lexicon with id %s cannot be found." % lexiconID
		logger.error( msg )
		if settings.DEBUG == True:
			print >> stderr, msg
		return
	except DatabaseError, exc:
		return
	query_str = li.query

	lexicon_tag = "Lexicon" + str( lexiconID )
	if settings.DEBUG == True:
		print >> stderr, "lexicon_tag: %s" % lexicon_tag

	# query ES to obtain the doc_ids
	es_baseurl = "http://" + settings.ELASTICSEARCH_HOST + ':' + str( settings.ELASTICSEARCH_PORT ) + '/'
	es_url = es_baseurl + settings.ES_INDEX
	es_url += "/_search/"

	date_begin = "%s-%s-%s" % ( begindate[0:4], begindate[4:6], begindate[6:8] )	# YYYYMMDD -> YYYY-MM-DD
	date_end   = "%s-%s-%s" % (   enddate[0:4],   enddate[4:6],   enddate[6:8] )	# YYYYMMDD -> YYYY-MM-DD

	query_str += " AND (paper_dc_date >= " + date_begin + " AND paper_dc_date <= " + date_end + ")"
	literal = False

	try:
		es_query_str = callperl( query_str, literal )	# call Perl: CQL -> ES JSON
	except:
		type, value, tb = exc_info()
		return cql2es_error( value )

	start_rec =   0			# ES start record: default =  0 (KB default = 1)
	count_rec = 100			# ES default chunk count = 10, BiLand KB retrieve was 20

	# loop in chunks
	nchunk = 0
	while True:
		params = \
		{
			'from'   : start_rec,
			'size'   : count_rec,
			'source' : es_query_str
		}

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

			resp_dict =  { "status" : "FAILURE", "msg" : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )

		if settings.DEBUG == True:
			print >> stderr, "chunk: %d" % nchunk
		#	print >> stderr, response.content
			print >> stderr, "url: %s" % es_url
			print >> stderr, "params: %s" % params

		es_dict = json.loads( response.content )

	#	if settings.DEBUG == True:
	#		print >> stderr, "es_dict:", es_dict
	#	for key in es_dict:
	#		print >> stderr, key

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

		doc_ids_list = []
		for h in range( len( hits_list ) ):
			hit = hits_list[ h ]
		#	print >> stderr, hit

		#	_index  = hit[ "_index" ]
		#	_type   = hit[ "_type" ]
			_id     = hit[ "_id" ]
			if settings.DEBUG == True:
				print >> stderr, "_id: %s" % _id

		#	_score  = hit[ "_score" ]
		#	_source = hit[ "_source" ]
			doc_ids_list.append( _id )

		# let xTAS add the tags for these documents
		doc_ids_str = ','.join( doc_ids_list )		# comma-separated string
		resp_dict = xtas_add_tags( doc_ids_str, lexicon_tag )
	#	resp_dict = {}

		if len( hits_list ) < count_rec:			# got less than we asked
			break
		else:
			start_rec += count_rec
			nchunk += 1

	resp_dict[ "hits_total" ] = "%d" % hits_total

	return resp_dict

# [eof]
