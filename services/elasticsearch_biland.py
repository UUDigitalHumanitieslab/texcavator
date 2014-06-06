# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		elasticsearch.py
Version:	0.23
Goal:		ElasticSearch functions

def es_queryid2esurl( lexiconID, collection, es_path )
def query2docids( lexicon_id, collection, date_begin, date_end )
def query2docidsdate( lexicon_id, collection, date_begin, date_end )
def es_doc_count( req_dict )
def elasticsearch_htmlresp( collection, start_rec, es_dict, prev_next )
def search_xtas_elasticsearch( request )
def retrieve_xtas_elasticsearch( request )

FL-15-Feb-2013: Created
FL-04-Jul-2013: -> BILAND app
FL-19-Dec-2013: Changed
"""

from sys import stderr, exc_info
from datetime import date
import requests
from lxml import etree
from lxml.html import fromstring

import json

#from celery.utils.log import get_task_logger	# celery-3: 
#logger = get_task_logger( __name__ ) 			# logger now defined at module level instead of function level

from django.conf import settings
from django.http import HttpResponse

from lexicon.download import get_es_chunk
from lexicon.models import LexiconItem
from services.cql2es import cql2es_error, callperl
from services.request import request2article_types, request2article_distrib, request2parms, is_literal
from services.xtas import xtas_add_tags

from es import get_document_ids, daterange2dates
from lexicon.utils import get_query

ES_CHUNK_SIZE = 2000


def es_queryid2esurl( lexiconID, collection, es_path ):
	"""\
	Create a CQL query, and translate it to an ES query
	"""
	if settings.DEBUG == True:
		print >> stderr, "es_queryid2esurl()", collection

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

	es_baseurl = "http://" + settings.ELASTICSEARCH_HOST + ':' + str( settings.ELASTICSEARCH_PORT ) + '/'
	if collection == settings.ES_INDEX_STABI:
		es_url = es_baseurl + settings.ES_INDEX_STABI
	else:
		es_url = es_baseurl + settings.ES_INDEX_KONBIB

	es_url += es_path

	return es_url, li.query



def query2docids( lexicon_id, collection, date_begin, date_end ):
	"""\
	Create and apply an ES query, and extract the document ids
	"""
	if settings.DEBUG == True:
		print >> stderr, "query2docids()", collection

	es_path = "/_search/"		# different syntax? YES, simpler
#	es_path = "/_count/"
	es_url, cql_query = es_queryid2esurl( lexicon_id, collection, es_path )

	cql_query += " AND (paper_dc_date >= " + date_begin + " AND paper_dc_date <= " + date_end + ")"

	# translate translate CQL -> ES
	literal = is_literal( cql_query )
	try:
		es_query_str = callperl( cql_query, literal )	# call Perl: CQL -> ES JSON
	except:
		etype, value, tb = exc_info()
		return cql2es_error( value, cql_query )

	if settings.DEBUG == True:
		print >> stderr, es_query_str

	start_rec =    0			# ES start record: default =  0 (KB default = 1)
	count_rec = ES_CHUNK_SIZE	# ES default chunk count = 10, BiLand KB retrieve was 20
	doc_ids_list = []
	nchunk = 0					# loop in chunks

	while True:
		params = \
		{
			"from"   : start_rec,
			"size"   : count_rec,
			"fields" : [ "_id" ],		# only need the doc ids
			"source" : es_query_str
		}

		try:
			response = requests.get( es_url, params = params )
		except:
			if settings.DEBUG == True:
				print >> stderr, "url: %s" % es_url
				print >> stderr, "params: %s" % params

			etype, value, tb = exc_info()
			msg = "ElasticSearch request failed: %s" % value
			if settings.DEBUG == True:
				print >> stderr, msg

			resp_dict =  { "status" : "FAILURE", "msg" : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )

		if settings.DEBUG == True:
			print >> stderr, "chunk: %d" % nchunk
			print >> stderr, response.content
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

		for h in range( len( hits_list ) ):
			hit = hits_list[ h ]
		#	print >> stderr, hit

		#	_index  = hit[ "_index" ]
		#	_type   = hit[ "_type" ]
			_id     = hit[ "_id" ]
		#	if settings.DEBUG == True:
		#		print >> stderr, "_id: %s" % _id

		#	_score  = hit[ "_score" ]
		#	_source = hit[ "_source" ]
			doc_ids_list.append( _id )

		if len( hits_list ) < count_rec:			# got less than we asked
			break
		else:
			start_rec += count_rec
			nchunk += 1

	return doc_ids_list



def query2docidsdate( lexicon_id, collection, date_begin, date_end ):
	"""\
	Get the document ids plus their date for the lexicon query and date range
	"""
	# this is called multiple times by the timeline
	if settings.DEBUG == True:
		print >> stderr, "query2docidsdate()", collection

	query, response = get_query(lexicon_id)

	date_range = {
        'lower': date_begin,
        'upper': date_end
	}

	doc_ids_list = get_document_ids(collection, 'doc', query, date_range)

	if settings.DEBUG:
	    print 'doc_ids_list:', doc_ids_list

	return doc_ids_list



#def es_doc_count( lexiconID, collection, date_begin, date_end ):
def es_doc_count( req_dict ):
	"""\
	Get the document count for the lexicon query and date range
	"""
	if settings.DEBUG == True: print >> stderr, "es_doc_count()"

	query_str, literal, date_begin, date_end, start_record, chunk_size, collection = request2parms( req_dict )

	lexiconID = req_dict[ "lexiconID" ]
	es_path = "/_search?search_type=count"
	es_url, cql_query = es_queryid2esurl( lexiconID, collection, es_path )

	cql_query += " AND (paper_dc_date >= " + date_begin + " AND paper_dc_date <= " + date_end + ")"
#	literal = is_literal( cql_query )

	# Add the KB document type[s] selection to the query
	doc_types = request2article_types( req_dict )
	if settings.DEBUG == True:
		print >> stderr, "type_query:", doc_types, collection
	if collection == settings.ES_INDEX_KONBIB and doc_types is not None:
		cql_query += doc_types

	# Add the KB document distribution[s] selection to the query
	distrib_types = request2article_distrib( req_dict )
	if settings.DEBUG == True:
		if not distrib_types:
			print >> stderr, "distrib_query:", "None", collection
		else:
			print >> stderr, "distrib_query:", distrib_types.encode( "utf-8" ), collection
	if collection == settings.ES_INDEX_KONBIB and distrib_types is not None:
		cql_query += distrib_types

	if settings.DEBUG == True: print >> stderr, cql_query.encode( "utf-8" )

	try:
		es_query_str = callperl( cql_query, literal )	# call Perl: translate CQL -> ES JSON
	except:
		type, value, tb = exc_info()
		status = "error"
		msg = "CQL to ElasticSearch conversion error: %s" % value
		hits_total = 0
		return status, msg, hits_total

	params = { 'source' : es_query_str }

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

		status = "error"
		hits_total = 0
		return status, msg, hits_total


	if settings.DEBUG == True:
	#	print >> stderr, response.content
		print >> stderr, "url: %s" % es_url
		print >> stderr, "params: %s" % params

	es_dict = json.loads( response.content )
	if settings.DEBUG == True:
		print >> stderr, es_dict

	try:
		status = es_dict[ "status" ]
		if settings.DEBUG == True:
			print >> stderr, "status:", status
		msg = es_dict[ "error" ]
		hits_total = 0
		return status, msg, hits_total
	except:
		status = "ok"
		msg = ""

	took      = es_dict[ "took" ]
	timed_out = es_dict[ "timed_out" ]
	_shards   = es_dict[ "_shards" ]
	hits      = es_dict[ "hits" ]

	_shards_total      = _shards[ "total" ]
	_shards_successful = _shards[ "successful" ]
	_shards_failed     = _shards[ "failed" ]

	hits_total     = int( hits[ "total" ] )
#	hits_max_score = hits[ "max_score" ]
	hits_list      = hits[ "hits" ]

	return status, msg, hits_total



def elasticsearch_htmlresp( collection, start_record, chunk_size, es_dict ):
	"""Create HTML response from ElasticSearch request"""
	if settings.DEBUG == True:
		print >> stderr, "elasticsearch_htmlresp()"

	try:
		took      = es_dict[ "took" ]
		timed_out = es_dict[ "timed_out" ]
		_shards   = es_dict[ "_shards" ]
		hits      = es_dict[ "hits" ]
	except:
		print >> stderr, es_dict

	try:
		_shards_total      = _shards[ "total" ]
		_shards_successful = _shards[ "successful" ]
		_shards_failed     = _shards[ "failed" ]
	except:
		_shards_total      = -1
		_shards_successful = 0
		_shards_failed     = -1

	hits_total     = hits[ "total" ]
	hits_max_score = hits[ "max_score" ]
	hits_list      = hits[ "hits" ]
	hits_retrieved = len( hits_list )

	if settings.DEBUG == True:
		print >> stderr, "took:", took
		print >> stderr, "timed_out:", timed_out

		print >> stderr, "_shards_total:", _shards_total
		print >> stderr, "_shards_successful:", _shards_successful
		print >> stderr, "_shards_failed:", _shards_failed

		print >> stderr, "hits_total", hits_total
		print >> stderr, "hits_max_score", hits_max_score
		print >> stderr, "hits_list", len( hits_list )


	html_str = '<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head>'
	html_str += '<body>'
	if hits_retrieved != hits_total:	# did not get everything
		if start_record > 1:
			have_prev = True
		else:
			have_prev = False

		if start_record + chunk_size < hits_total:
			have_next = True
		else:
			have_next = False

		href_pref = '<a href="javascript:nextResults(-' + str( chunk_size ) + ');">previous</a>'
		href_next = '<a href="javascript:nextResults(+' + str( chunk_size ) + ');">next</a>'

		html_str += '<span style="float:right">'
		if have_prev == True and have_next == True:
			html_str = html_str + href_pref + ' | ' +  href_next
		elif have_prev == True:
			html_str = html_str + href_pref
		elif have_next == True:
			html_str = html_str + href_next
		html_str += '</span>'

	if hits_total == 0:
		html_str += '<p>Found ' + "%s" % hits_total + ' records.'
	else:
		html_str += '<p>Found ' + "%s" % hits_total + ' records, '
		html_str += 'max score = ' + "%1.2f" % hits_max_score + '.</p>'

	html_str += '<ol start="' + '%s' % start_record + '">'

	datastore = settings.XTAS_DATASTORE

	for h in range( hits_retrieved ):
		hit = hits_list[ h ]
		if settings.DEBUG == True:
			print >> stderr, hit

	#	_index  = hit[ "_index" ]
	#	_type   = hit[ "_type" ]
		_id     = hit[ "_id" ]
		_score  = hit[ "_score" ]
	#	_source = hit[ "_source" ]

		print >> stderr, hit

		if collection == settings.ES_INDEX_KONBIB:
			article_dc_title       = hit[ "fields" ][ "article_dc_title" ][0]
			paper_dcterms_temporal = hit[ "fields" ][ "paper_dcterms_temporal" ][0]
			paper_dcterms_spatial  = hit[ "fields" ][ "paper_dcterms_spatial" ][0]
		else:
			try:
				article_dc_title = hit[ "fields" ][ "article_dc_title" ][0]
			except:
				article_dc_title = ""
			paper_dcterms_temporal = ""
			paper_dcterms_spatial  = ""

		try:
			zipfile = hit[ "fields" ][ "zipfile" ][0]
		except:
			zipfile = ""

		paper_dc_title = hit[ "fields" ][ "paper_dc_title" ][0]
		paper_dc_date  = hit[ "fields" ][ "paper_dc_date" ][0]

		item_str = "<li>"
	#	item_str += '<a href=javascript:dojo.publish("/es/record/selected",["' + _id + '"]); '
	#	item_str += '<a href=javascript:retrieveRecord("' + _id + ',' + datastore + '"); '
		item_str += '<a href=javascript:retrieveRecord("' + datastore + '","' + collection + '","' + _id + '","' + zipfile + '"); '

		if len( article_dc_title ) > 45:	# limit displayed title length
			item_str += 'title=' + article_dc_title + '><b>' + article_dc_title[ 0:45 ] + '</b>...</a>'
		else:
			item_str += 'title=' + article_dc_title + '><b>' + article_dc_title + '</b></a>'

		item_str += '<br>' + paper_dc_title
		item_str += '<br>' + paper_dc_date

		if paper_dcterms_temporal != "": item_str += ', ' + paper_dcterms_temporal
		if paper_dcterms_spatial  != "": item_str += ', ' + paper_dcterms_spatial

		item_str += ' [score: '
		item_str += "%1.2f" % _score
		item_str += ']'

		item_str += "</li>"
		html_str += item_str
	#	break

	html_str += '</ol></body>'

	html = fromstring( html_str )
	html_str = etree.tostring(html, pretty_print=True)

#	if settings.DEBUG == True:
#		print >> stderr, html_str
	return html_str



def search_xtas_elasticsearch( request, type_query ):
	"""Do ElasticSearch request"""
	if settings.DEBUG == True:
		print >> stderr, "search_xtas_elasticsearch()"

	query_str, literal, date_begin, date_end, start_record, chunk_size, collection = request2parms( request.REQUEST )
	cql_query_save = query_str				# before adding other stuff

	# Add the KB document type[s] selection to the query
	doc_types = request2article_types( request.REQUEST )
	if settings.DEBUG == True:
		print >> stderr, "type_query", doc_types
	if collection == settings.ES_INDEX_KONBIB and doc_types is not None:
		query_str += doc_types

	# Add the KB document distribution[s] selection to the query
	distrib_types = request2article_distrib( request.REQUEST )
	if settings.DEBUG == True and distrib_types is not None:
		print >> stderr, "distrib_query", distrib_types.encode( "utf-8" )
	if collection == settings.ES_INDEX_KONBIB and distrib_types is not None:
		query_str += distrib_types


	# Add the date range
	query_str += " AND (paper_dc_date >= " + date_begin + " AND paper_dc_date <= " + date_end + ")"

	try:
		es_query_str = callperl( query_str, literal )	# call Perl: CQL -> ES JSON
	except:
		etype, value, tb = exc_info()
		return cql2es_error( value, query_str )

	if settings.DEBUG == True:
		print >> stderr, "es_query: %s" % es_query_str.encode( "utf-8" )


	if len( cql_query_save ) > 0 and es_query_str == "{}":
		print >> stderr, "CQL to ElasticSearch translation error"

		html_str = '<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head>'
		html_str += '<body>'
		html_str += '<font color=red>CQL to ElasticSearch translation error</font>,</br>'
		html_str += 'please try to modify your query.</br>'
		html_str += 'E.g. use <b>OR</b> instead of just spaces between query words.'
		html_str += '</body>'
		return HttpResponse( html_str, mimetype = "text/html" )


	# limit the response fields to what we need; prefix "_source." is superfluous
	if collection == settings.ES_INDEX_KONBIB:
		fields = \
		[
			"article_dc_title",
			"paper_dcterms_temporal",
			"paper_dcterms_spatial",
			"paper_dc_title",
			"paper_dc_date"
		]
	elif collection == settings.ES_INDEX_STABI:
		fields = \
		[
			"article_dc_title",
			"paper_dc_title",
			"paper_dc_date",
			"zipfile"				# needed to disambiguate the StaBi scan dirname
		]
	else:
		fields = []

	params = \
	{
		"from"   : start_record,		# ES start record: default =  0 (KB default = 1)
		"size"   : chunk_size,		# ES default chunk count = 10, BiLand assumes 20
		"fields" : ",".join( fields ),	# supply as a string
		"source" : es_query_str
	}

	es_baseurl = "http://" + settings.ELASTICSEARCH_HOST + ':' + str( settings.ELASTICSEARCH_PORT ) + '/'
	if collection == settings.ES_INDEX_STABI:
		es_url = es_baseurl + settings.ES_INDEX_STABI
	else:
		es_url = es_baseurl + settings.ES_INDEX_KONBIB
	es_url += "/_search/"

	try:
		response = requests.get( es_url, params = params )
	except:
		if settings.DEBUG == True:
			print >> stderr, "url: %s" % es_url
			print >> stderr, "params: %s" % params
		etype, value, tb = exc_info()
		msg = "ElasticSearch request failed: %s" % value
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict =  { "status" : "FAILURE", "msg" : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )


	if settings.DEBUG == True:
	#	print >> stderr, response.content
		print >> stderr, "url: %s" % es_url
		print >> stderr, "params: %s" % params

	es_dict = json.loads( response.content )
#	if settings.DEBUG == True:
#		print >> stderr, "es_dict:", es_dict
#	for key in es_dict:
#		print >> stderr, key

	html_str = elasticsearch_htmlresp( collection, start_record, chunk_size, es_dict )	# create HTML list response

	return HttpResponse( html_str, mimetype = "text/html" )



def retrieve_xtas_elasticsearch( request ):
	req_dict = request.REQUEST
	_id = req_dict[ "id" ]
	if settings.DEBUG == True:
		print >> stderr, "_id:", _id

	try:
		collection = req_dict[ "collection" ]
	except:
		collection = settings.ES_INDEX_KONBIB

	es_baseurl = "http://" + settings.ELASTICSEARCH_HOST + ':' + str( settings.ELASTICSEARCH_PORT ) + '/'
	if collection == settings.ES_INDEX_STABI:
		es_url = es_baseurl + settings.ES_INDEX_STABI
		es_url += '/'
		es_url += settings.ES_INDEX_DOCTYPE_STABI
		es_url += '/'
	else:
		es_url = es_baseurl + settings.ES_INDEX_KONBIB
		es_url += '/'
		es_url += settings.ES_INDEX_DOCTYPE_KONBIB
		es_url += '/'

	es_url += _id

	try:
		response = requests.get( es_url )
	except:
		if settings.DEBUG == True:
			print >> stderr, "url: %s" % es_url

		etype, value, tb = exc_info()
		msg = "ElasticSearch request failed: %s" % value
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict =  { "status" : "FAILURE", "msg" : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )


	if settings.DEBUG == True:
		print >> stderr, "url: %s" % es_url

	es_dict = json.loads( response.content )

	if settings.DEBUG == True:
		print >> stderr, es_dict

	html = '<?xml version="1.0" encoding="UTF-8"?>\n'
	try:
		html += es_dict[ "_source" ][ "text_content" ]
	except:
		etype, value, tb = exc_info()
		msg = "ElasticSearch request failed: %s" % value
		if settings.DEBUG == True:
			print >> stderr, msg
			print >> stderr, es_dict
		html += msg

	resp_dict = \
	{
		"status" : "ok",
		"text" : html

	}
	json_list = json.dumps( resp_dict )
	ctype = 'application/json; charset=UTF-8'
	return HttpResponse( json_list, content_type = ctype )

# [eof]
