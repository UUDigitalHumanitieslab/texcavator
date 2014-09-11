# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Copyright:	Daan Odijk, Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/views.py
Version:	0.41
Goal:		services/views

def index( request )
def daterange_lexicon( request, lexiconID, beginDate, endDate )
def add_document_tag( docID, tag )
def get_docids( tags_str )
def delete_xtas_tags( tags )
def aggregation(request, lexiconID)
def item(request, id)
def dayStatistics(request)
def bursts( request, lexiconID, collection = settings.ES_INDEX, resolution = "year" )
def bursts_zoom( request, lexiconID, datetuple )
def timestamp_refresh( request )
def stopwords_get_editglob( username ):
def stopwords_save( request )
def stopwords_delete( request )
def stopwords_retrieve_string( request )
def stopwords_retrieve_editglob( request )
def stopwords_retrieve_table( request )

DO-%%-%%%-2011: Created
FL-09-Dec-2011: No more limit of 10 shown lexica
FL-10-Jan-2012: Filter by username
FL-15-Feb-2012: Save with user/group name
FL-04-Apr-2012: With save, check not only title but also user
FL-27-Aug-2012: Timeline functions from Infiniti demo
FL-28-Sep-2012: Apply daterange to timeline request
FL-06-Nov-2012: Stopwords in db
FL-04-Jan-2013: update of remove metadata & ocrdata
FL-07-Feb-2013: No more default date limits
FL-10-Sep-2013: Changed
"""

import os
from sys import stderr, exc_info
import requests
import collections, datetime
from operator import itemgetter

import logging
logger = logging.getLogger( __name__ )

import json

from django.conf import settings

try:
	from lxml import etree
	if settings.DEBUG == True:
		print >> stderr, "running with lxml.etree"
except ImportError:
	try:
		# Python 2.5
		import xml.etree.cElementTree as etree
		if settings.DEBUG == True:
			print >> stderr, "running with cElementTree on Python 2.5+"
	except ImportError:
		try:
			# Python 2.5
			import xml.etree.ElementTree as etree
			if settings.DEBUG == True:
				print >> stderr, "running with ElementTree on Python 2.5+"
		except ImportError:
			try:
				# normal cElementTree install
				import cElementTree as etree
				if settings.DEBUG == True:
					print >> stderr, "running with cElementTree"
			except ImportError:
				try:
					# normal ElementTree install
					import elementtree.ElementTree as etree
					if settings.DEBUG == True:
						print >> stderr, "running with ElementTree"
				except ImportError:
					if settings.DEBUG == True:
						print >> stderr, "Failed to import ElementTree from any known place"

from django.contrib import auth
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from lexicon.models import LexiconItem, LexiconArticle, StopWordOld, DayStatistic

from services.elasticsearch_biland import query2docidsdate


@csrf_exempt
def index( request ):
	if request.method == "GET":
		if settings.DEBUG == True:
			print >> stderr, "lexicon/views.py/index() GET"
		# get lexicons
		logger.debug( "GET query list", extra = request.META )

		try:
			username = request.REQUEST[ "username" ]
		except( KeyError ):
			username = ""
		msg = "username: %s" % username
		if settings.DEBUG == True:
			print >> stderr, msg
		logger.debug( msg, extra = request.META )

		try:
			lexicon_items = LexiconItem.objects.all().order_by( '-created' )
			if username == '':
				lexicon_items = LexiconItem.objects.none()					# hide all
			else:
				lexicon_items = lexicon_items.filter( user = username )		# show only those of login user

		#	for li in lexicon_items:
		#		print >> stderr, "%2s %s %s" % ( li.id, li.created, li.title )

			resp_data = serializers.serialize( "json", lexicon_items, ensure_ascii = False )
			resp_dict = { 'status' : "SUCCESS", 'msg' : "", 'lexicon_items' : resp_data }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )
		except:
			type, value, tb = exc_info()
			msg = "Queries could not be retrieved: %s" % value
			if settings.DEBUG == True:
				print >> stderr, msg
			logger.debug( "%s [%s]", title, msg, extra = request.META )
			resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )

	elif request.method == "POST":
		if settings.DEBUG == True:
			print >> stderr, "lexicon/views.py/index() POST"
		# save query as new lexicon
		req_data = json.loads( request.raw_post_data )
		user      = req_data[ "fields" ][ "user" ]
		title     = req_data[ "fields" ][ "title" ]
		overwrite = req_data[ "fields" ][ "overwrite" ]

		# check whether lexicon title already exists for this user
		try:
			qset = LexiconItem.objects.filter( title = title, user = user )
		except:
			type, value, tb = exc_info()
			msg = "Query could not be saved: %s" % value
			if settings.DEBUG == True:
				print >> stderr, msg
			logger.debug( "%s [%s]", title, msg, extra = request.META )
			resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )

		count = qset.count()
	#	print >> stderr, "lexicon items:", count

		if count == 1:
			if overwrite == True:	# overwrite existing query
				lexiconItem = LexiconItem.objects.get( title = title, user = user )
				if settings.DEBUG == True:
					print >> stderr, "query title:", lexiconItem.title
				query = req_data[ "fields" ][ "query" ]
				if settings.DEBUG == True:
					print >> stderr, "old query:", lexiconItem.query
					print >> stderr, "new query:", query

				try:
					lexiconItem.query = query
					lexiconItem.save()
				except:
					type, value, tb = exc_info()
					msg = "Lexicon could not be saved: %s" % value
					if settings.DEBUG == True:
						print >> stderr, msg
					logger.debug( "%s [%s]", title, msg, extra = request.META )
					resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
					json_list = json.dumps( resp_dict )
					ctype = 'application/json; charset=UTF-8'
					return HttpResponse( json_list, content_type = ctype )

				try:
					removetags = req_data[ "fields" ][ "removetags" ]
				except:
					removetags = False
				if settings.DEBUG == True:
					print >> stderr, "removetags:", removetags

				if removetags:
					lexiconTag = "Lexicon" + str( lexiconItem.id )
				#	print >> stderr, "lexiconTag:", lexiconTag
				delete_xtas_tags( lexiconTag )

				resp_data = serializers.serialize( "json", [ lexiconItem ], ensure_ascii = False )
				resp_dict = { 'status' : "SUCCESS", 'msg' : "", 'data' : resp_data }
				json_list = json.dumps( resp_dict )
				ctype = 'application/json; charset=UTF-8'
				return HttpResponse( json_list, content_type = ctype )
			else:
				msg = "Lexicon title already exists"
				if settings.DEBUG == True:
					print >> stderr,msg
				logger.debug( "%s [%s]", title, msg, extra = request.META )
				resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
				json_list = json.dumps( resp_dict )
				ctype = 'application/json; charset=UTF-8'
				return HttpResponse( json_list, content_type = ctype )

		elif count == 0:			# create new lexicon item
			newItem = LexiconItem()
			newItem.user  = req_data[ "fields" ][ "user" ]
			newItem.group = "biland"
			newItem.title = title
			newItem.query = req_data[ "fields" ][ "query" ]

			try:
				newItem.save()
				logger.debug( "New lexicon item: %s [%s]", newItem.title, newItem.query, extra = request.META )
			#	return HttpResponse( serializers.serialize( "json", [ newItem ], ensure_ascii = False ) )
				resp_data = serializers.serialize( "json", [ newItem ], ensure_ascii = False )
				resp_dict = { 'status' : "SUCCESS", 'msg' : "", 'data' : resp_data }
				json_list = json.dumps( resp_dict )
				ctype = 'application/json; charset=UTF-8'
				return HttpResponse( json_list, content_type = ctype )
			except:
				type, value, tb = exc_info()
				msg = "Lexicon could not be saved: %s" % value
				if settings.DEBUG == True:
					print >> stderr, msg
				logger.debug( "%s [%s]", title, msg, extra = request.META )
				resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
				json_list = json.dumps( resp_dict )
				ctype = 'application/json; charset=UTF-8'
				return HttpResponse( json_list, content_type = ctype )

		else:
			msg = "bad lexicon count: %d " % count
			if settings.DEBUG == True:
				print >> stderr,msg
			logger.debug( "Lexicon could not be saved: %s [%s]", title, msg, extra = request.META )
			resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )

	else:
		if settings.DEBUG == True:
			print >> stderr, "lexicon/views.py/index() 404"
		return Http404



@csrf_exempt
def aggregation(request, lexiconID):
	li = get_object_or_404(LexiconItem, pk=lexiconID)
	if request.method == "GET" and request.GET.has_key("field"):
		from django.db.models import Count
		if request.GET.has_key("extra"):
			values = li.documents.values(request.GET["field"], request.GET["extra"])
		else:
			values = li.documents.values(request.GET["field"])
		aggregation = values.annotate(Count(request.GET["field"]))
		if request.GET.has_key("order"):
			aggregation = aggregation.order_by(request.GET["order"])
		return HttpResponse(aggregation)
	return Http404



@csrf_exempt
def item(request, id):
	li = get_object_or_404(LexiconItem, pk=id)
	if request.method == "PUT":
		for obj in serializers.deserialize("json", request.raw_post_data, ensure_ascii=False):
			if(obj.object.pk == int(id)):
				obj.save()
				logger.debug("Update lexicon item %s: %s [%s]", id, obj.object.title, obj.object.query, extra=request.META)
				return HttpResponse(request.raw_post_data)
		return Http404
	
	json = serializers.serialize("json", [li], ensure_ascii=False)

	if request.method == "DELETE":
		# delete date_range lexicon, if it exists
		dr_title = li.title + "_daterange"
		try:
			dr_li = LexiconItem.objects.get( title = dr_title )
			delete_tag = True	# we have a daterange lexicon
		except LexiconItem.DoesNotExist:
			delete_tag = False	# no daterange lexicon

		if delete_tag == True:
			try:
				dr_li.delete()	# delete this lexicon
			#	print >> stderr, "Lexicon with title %s was deleted" % dr_title
				logger.debug( "Delete lexicon item %s: %s [%s]", dr_li.id, dr_title, li.query, extra=request.META )
			except LexiconItem.DoesNotExist:
			#	print >> stderr, "Lexicon with title %s could not be deleted" % dr_title
				logger.debug( "Lexicon with title %s could not be deleted", dr_title, extra=request.META )

		tag = "Lexicon" + str( id )
	#	logger.info("Tag %s was NOT deleted from xTAS", tag, extra=request.META)
		# delete this tag from the lexicon OCR docs
		delete_xtas_tags( tag )
		logger.info("Tag %s was deleted from xTAS", tag, extra=request.META)

		li.delete()
		logger.debug( "Delete lexicon item %s: %s [%s]", id, li.title, li.query, extra=request.META )

	else:
		logger.debug("GET lexicon item %s: %s [%s]", id, li.title, li.query, extra=request.META)

	return HttpResponse( json )



# This requires the table DayStatistic, which should be made with the management 
# command gatherstatistics.py which gathers the required info from the KB. 
# This is only needed for normalization. 
def dayStatistics(request):
	if settings.DEBUG == True:
		print >> stderr, "dayStatistics()"

	from django.db.models import Sum
	values = DayStatistic.objects.values('date','count').all()

	aggregation = {}
	for year in range(1850, 1945):
		aggregation[year] = 0

	for value in values:
		aggregation[value['date'].year] += value['count']

	return HttpResponse( json.dumps( aggregation ) )



#@cache_page(60 * 15)	# name 'cache_page' is not defined
@csrf_exempt
def bursts( request, lexiconID, collection = settings.ES_INDEX, resolution = "year" ):
	if settings.DEBUG == True:
		print >> stderr, "lexicon/bursts() lexiconID:", lexiconID, "resolution:", resolution

	req_dict = request.REQUEST

	try:
		collection = req_dict[ "collection" ]
	except:
		collection = settings.ES_INDEX

	try:
		normalize_str = req_dict[ "normalize" ]
	except:
		normalize_str = ''

	if normalize_str == '1':
		normalize = True
	elif  normalize_str == '0':
		normalize = False
	else:
		normalize = False

	bg_smooth = False

	"""
	try:
		burstdetect_str = req_dict[ "burstdetect" ]
	except:
		burstdetect_str = ''

	if burstdetect_str == '1':
		burstdetect = True
	elif  burstdetect_str == '0':
		burstdetect = False
	else:
		burstdetect = False
	print >> stderr, "burstdetect ", burstdetect
	"""

	try:
		begin = req_dict[ "begindate" ]
	except:
	#	begin = str( SRU_DATE_LIMITS[ 0 ] )		# "18500101"
		raise Exception( "Missing daterange parameter" )

	try:
		end = req_dict[ "enddate" ]
	except:
	#	end = str( SRU_DATE_LIMITS[ 1 ] )		# "19451231"
		raise Exception( "Missing daterange parameter" )

	begindate = datetime.date( year = int( begin[0:4] ), month = int( begin[4:6] ), day = int( begin[6:8] ) )
	enddate   = datetime.date( year = int( end[0:4] ),   month = int( end[4:6] ),   day = int( end[6:8] ) )

	logger.debug( "Getting bursts %s", lexiconID, extra = request.META )
	li = get_object_or_404( LexiconItem, pk = lexiconID )

	# normalization and/or smoothing
	values = DayStatistic.objects.values( 'date', 'count' ).all()
	date2countC = {}
	for dc in values:
		if dc[ 'date' ] <= enddate and dc[ 'date' ] >= begindate:
			date2countC[ dc[ 'date' ] ] = dc[ 'count' ]

	date_begin = "%s-%s-%s" % ( begin[0:4], begin[4:6], begin[6:8] )    # YYYYMMDD -> YYYY-MM-DD
	date_end   = "%s-%s-%s" % (   end[0:4],   end[4:6],   end[6:8] )    # YYYYMMDD -> YYYY-MM-DD

	documents_raw = query2docidsdate( lexiconID, collection, date_begin, date_end )
	documents = sorted( documents_raw, key = lambda k: k[ "date" ]) 
	doc2date = {}
	for doc in documents:
	    doc_date = doc[ "date" ]
	    if doc_date <= enddate and doc_date >= begindate:
		# print >> stderr, doc_date
	    	doc2date[ doc[ "identifier" ] ] = doc_date

	if settings.DEBUG == True:
		print >> stderr, "burst parameters:"
		print >> stderr, "len doc2date:", len(doc2date)				# can be big
		#print >> stderr, "(doc2date not shown)"
		print >> stderr, "doc2relevance: {}"
		print >> stderr, "len date2countC:", len(date2countC)		# can be big
		#print >> stderr, "(date2countC not shown)"
		print >> stderr, "normalize:", normalize
		print >> stderr, "bg_smooth:", False
		print >> stderr, "resolution:", resolution

	import lexicon.burstsdetector.bursts as bursts

	burstsList = bursts.bursts( doc2date, {}, date2countC = date2countC, normalise = normalize, bg_smooth = bg_smooth, resolution = resolution )[ 0 ]
#	print >> stderr, "burstsList:", burstsList

	date2count = {}
#	max_doc_count = 0
#	max_doc_float = 0.0
	for date, tup in burstsList.iteritems():
		doc_float, zero_one, index, limit, doc_count, doc_ids = tup
		if doc_count != 0:
		#	max_doc_count = max( max_doc_count, doc_count )
		#	max_doc_float = max( max_doc_float, doc_float )

		#	print >> stderr, "date:", date, "tup:", tup
			# e.g.: d: 1942-09-22 k: (2.0, 0, 33866, None, 2, [u'ddd:010319673:mpeg21:a0073:ocr', u'ddd:010020411:mpeg21:a0062:ocr'])
		#	print >> stderr, "doc_float:", doc_float, "zero_one:", zero_one, "index:", index, "limit:", limit, "doc_count:", doc_count, "doc_ids:", doc_ids
		#	date2count[ date.isoformat() ] = tup
			doc_float = float( "%.1f" % doc_float )			# less decimals
			if limit: 										# not None
				limit = float( "%.1f" % limit )				# less decimals
			date2count[ date.isoformat() ] = ( doc_float, zero_one, index, limit, doc_count, doc_ids )

	return HttpResponse( json.dumps( date2count ) )



@csrf_exempt
def bursts_zoom( request, lexiconID, datetuple ):
	if settings.DEBUG == True:
		print >> stderr, "bursts_zoom()"

	import lexicon.bursts as bursts

	begin, end = datetuple
	li = get_object_or_404( LexiconItem, pk = lexiconID )
	values = DayStatistic.objects.values( 'date','count' ).all()

	date2countC = {}
	for l in values:
		if l[ 'date' ] <= end and l[ 'date' ] >= begin:
			date2countC[ l[ 'date' ] ] = l[ 'count' ]

	doc2date = {}
	for doc in li.documents.all():
		if doc.date <= end and doc.date >= begin:
			doc2date[ doc.identifier ] = doc.date

	# have some kind of indicator if days, years, months or week normalisation.
	burstsList, dummy = bursts.bursts( doc2date, {}, date2countC = date2countC, normalise = True, bg_smooth = True, resolution = 'year')
	date2count = {}
	for d, k in burstsList.iteritems():
		date2count[ d.isoformat() ] = k

	return HttpResponse( json.dumps( date2count ) )



@csrf_exempt
def timestamp_refresh( request ):
	if settings.DEBUG == True:
		print >> stderr, "timestamp_refresh()"

	req_dict = request.REQUEST		# searches POST first, then GET

	try:
		username  = req_dict[ 'username' ]
		password  = req_dict[ 'password' ]
		lexiconID = req_dict[ 'lexiconID' ]

	except( KeyError ):
		msg = "key error on 'username', ,'password', 'lexiconID' or 'refresh'"
		if settings.DEBUG == True:
			print>> stderr, msg

		resp_dict = \
		{
			'status' : 'FAILURE',
			'msg'    : msg
		}
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	try:
		li = LexiconItem.objects.get( id = lexiconID )
	except:
		type, value, tb = exc_info()
		msg =  "Lexicon could not be retrieved: %s" % value
		if settings.DEBUG == True:
			print >> stderr,msg
		logger.debug( "Lexicon could not be retrieved: %s [%s]", title, value, extra = request.META )
		resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	user = auth.authenticate( username = username, password = password )
	if user is None:
		if settings.DEBUG == True:
			print >> stderr, "user:", "None"
		resp_dict = \
		{
			'status' : "FAILURE",
			'msg'    : "unrecognized user"
		}
		return HttpResponse( json.dumps( resp_dict ) )

	if li.user != username:
		if settings.DEBUG == True:
			print >> stderr, "user:", li.user
		resp_dict = \
		{
			'status' : "FAILURE",
			'msg'    : "wrong lexicon user"
		}
		return HttpResponse( json.dumps( resp_dict ) )


	updated = datetime.datetime.now()
	dt_string = updated.strftime( "%Y-%m-%dT%H:%M:%02S" )

	try:
		li.created = updated
		li.save()
	except:
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "Timestamp could not be updated: %s" % value
		logger.debug( "Timestamp could not be updated: %s [%s]", title, value, extra = request.META )
		resp_dict = { 'status' : 'FAILURE', 'msg' : value }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	resp_dict = \
	{
		"status" : "SUCCESS",
		"timestamp" : dt_string
	}
	return HttpResponse( json.dumps( resp_dict ) )



def stopwords_get_editglob( username ):
	if settings.DEBUG == True: print >> stderr, "stopwords_get_editglob()"

	# who can edit global stopwords ?
	if username == "aclaan" or \
		username == "jdekruif":
		editglob = True
	else:
		editglob = False

	return editglob



@csrf_exempt
def stopwords_save( request ):
	if settings.DEBUG == True: print >> stderr, "stopwords_save()"

	req_dict = request.REQUEST		# searches POST first, then GET

	try:
		username = req_dict[ 'username' ]
		password = req_dict[ 'password' ]
		stopword = req_dict[ 'stopword' ]
		category = req_dict[ 'category' ]
		swclean  = req_dict[ 'clean' ]
	except( KeyError ):
		msg = "key error on 'username', 'password', 'stopword', 'category', or 'clean'"
		if settings.DEBUG == True:
			print>> stderr, msg
		resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	if settings.DEBUG == True:
		print >> stderr, "username:", username
		print >> stderr, "password:", password
		print >> stderr, "stopword:", stopword.encode( 'utf-8' )
		print >> stderr, "category:", category
		print >> stderr, "swclean:",  swclean
	
	if swclean == "1":
		delete_doublures = True		# remove superfluous multiples of stopwords
	else:
		delete_doublures = False

	user = auth.authenticate( username = username, password = password )
	if user is None:
		if settings.DEBUG == True:
			print >> stderr, "user:", "None"
	else:
		if settings.DEBUG == True:
			print >> stderr, "user_id:", user.id

	stopwordItem = StopWord()
	stopwordItem.word = stopword.lower()	# treating stopwords case-insentive

	if category == "system":	# power user
		if stopwords_get_editglob( username ) == True:	# has the user permission to store a system stopword?
			stopwordItem.user = None
		else:
			msg = "User %s not authorized to store global stopword" % username
			if settings.DEBUG == True:
				print>> stderr, msg
			resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )
	else:		# regular user
		stopwordItem.user = user

	try:
		lexiconID = req_dict[ 'lexiconID' ]
		if settings.DEBUG == True:
			print >> stderr, "lexiconID:", lexiconID
		lexicon = LexiconItem.objects.get( id = lexiconID )
		if settings.DEBUG == True:
			print >> stderr, "lexicon_id:", lexicon.id
		stopwordItem.query = lexicon
	except( KeyError ):
		lexiconID = None
		stopwordItem.query = None

	# Does the stopword already exists 'globally' (user = None, query = None)? 
	# Then it makes no sense to add it for given users or queries. 
	try:
		qset = StopWord.objects.all().filter( user = None, query = None, word = stopword )
		wordcount = qset.count()
	#	print >> stderr, "count:", wordcount
		if wordcount == 0:
			if settings.DEBUG == True:
				print >> stderr, "stopword '%s' does not exist for all users and all queries" % stopword
		else:
			msg = "stopword '%s' already exists for all users and all queries" % stopword
			if settings.DEBUG == True:
				print >> stderr, msg
			resp_dict = { "status" : "FAILURE", "msg" : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )
	except:
		type, value, tb = exc_info()
		msg = "stopword '%s' could not be saved: %s" % ( stopword, value )
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = { "status" : "FAILURE", "msg" : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	# Does the stopword already exists for this user with query = None?
	# Then it makes no sense to add it again for individual queries
	try:
		# select_related(): follow the ForeignKey
		qset = StopWord.objects.select_related().filter( user__username = username, query = None, word = stopword )
		wordcount = qset.count()
	#	print >> stderr, "count:", wordcount
		if wordcount == 0:
			if settings.DEBUG == True:
				print >> stderr, "stopword '%s' does not exist for user '%s' and all user queries" % ( stopword, username )
		else:
			msg = "stopword '%s' already exists for user '%s' and all user queries" % ( stopword, username )
			if settings.DEBUG == True:
				print >> stderr, msg
			resp_dict = { "status" : "FAILURE", "msg" : msg }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )
	except:
		type, value, tb = exc_info()
		msg = "stopword '%s' could not be saved: %s" % ( stopword, value )
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = { "status" : "FAILURE", "msg" : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	# Does the stopword already exists for this user with this query?
	if lexiconID != None:
		try:
			qset = StopWord.objects.select_related().filter( user__username = username, query__id = lexiconID, word = stopword )
			wordcount = qset.count()
		#	print >> stderr, "count:", wordcount
			if wordcount == 0:
				if settings.DEBUG == True:
					print >> stderr, "stopword '%s' does not exist for user '%s' and query '%s'" % ( stopword, username, stopwordItem.query )
			else:
				msg = "stopword '%s' already exists for user '%s' and query '%s'" % ( stopword, username, stopwordItem.query )
				if settings.DEBUG == True:
					print >> stderr, msg
				resp_dict = { "status" : "FAILURE", "msg" : msg }
				json_list = json.dumps( resp_dict )
				ctype = 'application/json; charset=UTF-8'
				return HttpResponse( json_list, content_type = ctype )
		except:
			type, value, tb = exc_info()
			msg = "stopword '%s' could not be saved: %s" % ( stopword, value )
			if settings.DEBUG == True:
				print >> stderr, msg

	try:
		stopwordItem.save()
	except:
		type, value, tb = exc_info()
		msg = "stopword '%s' could not be saved: %s" % ( stopword, value )
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = { 'status' : 'FAILURE', 'msg' :  msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	msg_clean = None
	if delete_doublures == True:
		status, msg_clean = stopwords_cleanup( username, stopword, lexiconID )
		if status != "SUCCESS":
			resp_dict = { 'status' : status, 'msg' : msg_clean }
			json_list = json.dumps( resp_dict )
			ctype = 'application/json; charset=UTF-8'
			return HttpResponse( json_list, content_type = ctype )


	msg = "stopword '%s' has been saved" % stopword
	if msg_clean:
		msg = msg + "; " + msg_clean
	if settings.DEBUG == True:
		print >> stderr, msg
	resp_dict = { 'status' : 'SUCCESS', 'msg' :  msg }
	json_list = json.dumps( resp_dict )
	ctype = 'application/json; charset=UTF-8'
	return HttpResponse( json_list, content_type = ctype )



def stopwords_cleanup( username, stopword, lexiconID ):
	"""delete doublures from stopword table for given stopword"""
	if settings.DEBUG == True: print >> stderr, "stopwords_cleanup()"

	# after a stopword save, there are 2 possibilities for doublures: 
	# -1- a certified user saved a stopword globally: all other occurrences can be removed
	# -2- a user saved a stopword for all his queries, so possible occurrences tied to queries can be removed

	# occurrences of this stopword
	try:
		qset_all = StopWord.objects.select_related().filter( word = stopword )
		wordcount = qset_all.count()
	except:
		type, value, tb = exc_info()
		msg = "problem retrieving '%s': %s" %  ( stopword, value )
		if settings.DEBUG == True: print >> stderr, msg
		status = "FAILURE"
		return status, msg

	# global stopwords
	qset_global = qset_all.filter( user__username = None, query__id = None )

	qset_remove_nonglob = StopWord.objects.none()			# default with empty qs
	if stopwords_get_editglob( username ) == True:
		# user can delete global stopwords
		global_count = qset_global.count()
		if global_count > 0:
			if global_count > 1:		# doublures of global stopword: must me cleaned
				if settings.DEBUG == True:
					print >> stderr, "stopwords_cleanup: %d global occurrences for stopword: %s" % ( global_count, stopword )
				# ...
			qset_remove_nonglob = qset_all.exclude( pk__in = qset_global )
		else:
			qset_remove_nonglob = StopWord.objects.none()	# default with empty qs

		if qset_remove_nonglob.count() > 0:
			if settings.DEBUG == True:
				print >> stderr, "%d non-global stopword occurrences to be removed..." % qset_remove_nonglob.count()

	# user stopwords
	qset_remove_user = StopWord.objects.none()				# default with empty qs
	if lexiconID == None:
		# stopword was saved for all user queries: remove query bound stopword for this user
		try:
			qset_remove_user = StopWord.objects.select_related().filter( user__username = username, word = stopword ).exclude( query__id = None )
			if settings.DEBUG == True:
				print >> stderr, "%d user stopword occurrences to be removed..." % qset_remove_user.count()
		except:
			type, value, tb = exc_info()
			msg = "problem retrieving '%s': %s" %  ( stopword, value )
			if settings.DEBUG == True: print >> stderr, msg
			status = "FAILURE"
			return status, msg

	# remove stopwords
	qset = qset_remove_nonglob | qset_remove_user
	for stopword in qset:
		if settings.DEBUG == True:
			print >> stderr, "deleting stopword:", stopword.word, "query:", stopword.query
		try:
			stopword.delete()
		except:
			type, value, tb = exc_info()
			msg = "problem deleting old '%s': %s" %  ( stopword, value )
			if settings.DEBUG == True: print >> stderr, msg
			status = "FAILURE"
			return status, msg

	status = "SUCCESS"
	if qset.count() == 1:
		msg = "1 stopword deleted"
	else:
		msg = "%d stopwords deleted" % qset.count()

	return status, msg



@csrf_exempt
def stopwords_delete( request ):
	if settings.DEBUG == True: print >> stderr, "stopwords_delete()"

	req_dict = request.REQUEST		# searches POST first, then GET

	try:
		username = req_dict[ 'username' ]
		password = req_dict[ 'password' ]
		pk_str   = req_dict[ 'pk' ]
	except( KeyError ):
		msg = "key error on 'username', 'password', or 'pk'"
		if settings.DEBUG == True:
			print>> stderr, msg
		resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	pk = int( pk_str )
	if settings.DEBUG == True:
		print >> stderr, "username:", username
		print >> stderr, "password:", password
		print >> stderr, "pk", pk

	user = auth.authenticate( username = username, password = password )
	if user is None:
		if settings.DEBUG == True:
			print >> stderr, "user:", "None"
	else:
		if settings.DEBUG == True:
			print >> stderr, "user_id:", user.id

	try:
		stopword = StopWord.objects.get( pk = pk )
		if settings.DEBUG == True:
			print >> stderr, "stopword:", stopword.word
	except:
		type, value, tb = exc_info()
		msg = "Stopword id %d exception: %s" % ( pk, value )
		if settings.DEBUG: print >> stderr, msg
		resp_dict = { 'status' : "FAILURE", 'msg' : msg }
		return HttpResponse( json.dumps( resp_dict ) )

	# is user allowed to delete this stopword?
	try:
		stop_user = stopword.user.username
	except:
		# no user: global stopword
		if stopwords_get_editglob( username ) == False:
			msg = "User %s is not allowed to delete stopword: %s" % (  username, stopword.word )
			resp_dict = { 'status' : "FAILURE", 'msg' : msg }
			return HttpResponse( json.dumps( resp_dict ) )
		else:
			stop_user = None

	if stopwords_get_editglob( username ) == True:
		pass		# power user can also delete stopwords of other users
	elif username != stop_user:
		msg = "User %s is not owner of stopword: %s" % (  username, stopword.word )
		resp_dict = { 'status' : "FAILURE", 'msg' : msg }
		return HttpResponse( json.dumps( resp_dict ) )

	try:
		stopword.delete()
	except:
		type, value, tb = exc_info()
		msg = "Stopword could not be deleted: %s" % value
		resp_dict = { 'status' : "FAILURE", 'msg' : msg }
		return HttpResponse( json.dumps( resp_dict ) )

	resp_dict = { 'status' : "SUCCESS" }
	return HttpResponse( json.dumps( resp_dict ) )



@csrf_exempt
def stopwords_retrieve_string( request ):
	if settings.DEBUG == True: print >> stderr, "stopwords_retrieve_string()"

	req_dict = request.REQUEST		# searches POST first, then GET

	try:
		username  = req_dict[ 'username' ]
		password  = req_dict[ 'password' ]
	except( KeyError ):
		msg = "key error on 'username', 'password', or 'lexiconID'"
		if settings.DEBUG == True:
			print >> stderr, msg

		resp_dict = \
		{
			'status' : 'FAILURE',
			'msg'    : msg
		}

		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	try:
		lexiconID = req_dict[ 'lexiconID' ]
	except( KeyError ):
		lexiconID = None	# cloud for single article can be without lexiconID

	user = auth.authenticate( username = username, password = password )
	if user is None:
		if settings.DEBUG == True:
			print >> stderr, "user:", "None"
		resp_dict = \
		{
			'status' : "FAILURE",
			'msg'    : "unrecognized user"
		}
		return HttpResponse( json.dumps( resp_dict ) )
	else:
		if settings.DEBUG == True:
			print >> stderr, "user_id:", user.id

	try:
		# select_related(): follow the ForeignKey into the corpus table; 
		# when that data is needed, no additional queries are needed (fast!).
		sw_qset = StopWord.objects.select_related().all()
	#	print >> stderr, "all stopwords:", sw_qset.count()

		# stopwords for all users and all queries
		sw_globq = sw_qset.filter( user = None, query = None )
	#	if settings.DEBUG == True: print >> stderr, "system stopwords:", sw_globq.count(), sw_globq

		# all stopwords for this user
		sw_qset = sw_qset.filter( user = user )
	#	print >> stderr, "all user stopwords:", sw_qset.count()

		# the stopwords for all queries (for this user)
		sw_uanyq = sw_qset.filter( query = None )
	#	print >> stderr, "user any query stopwords:", sw_uanyq.count(), sw_uanyq

		# the stopwords for this query (for this user)
		if lexiconID is not None:
			sw_thisq = sw_qset.filter( query__id = lexiconID )
			#	print >> stderr, "user query stopwords:", sw_thisq.count(), sw_thisq
		else:
			sw_thisq = StopWord.objects.none()
	except:
		type, value, tb = exc_info()
		msg = "Stopwords could not be retrieved: %s" % value
		resp_dict = { 'status' : "FAILURE", 'msg' : msg }
		return HttpResponse( json.dumps( resp_dict ) )

	sw_tot = sw_globq | sw_uanyq | sw_thisq		# merge the 3 query sets

	stoplist = []
	for sw in sw_tot:
	#	print >> stderr, sw.word, sw.query
	#	stoplist.append( sw.word ) 
		stoplist.append( sw.word.lower() )		# lowercase, -> case-insensitive feature request for xTAS
	stopwords = ','.join( stoplist )
#	print >> stderr, "stopwords:", stopwords

	resp_dict = \
	{
		'status'    : "SUCCESS",
		'stopwords' : stopwords
	}

	return HttpResponse( json.dumps( resp_dict ) )



@csrf_exempt
def stopwords_retrieve_editglob( request ):
	if settings.DEBUG == True: print >> stderr, "stopwords_retrieve_editglob()"

	req_dict = request.REQUEST

	try:
		username = req_dict[ 'username' ]
		password = req_dict[ 'password' ]
	except( KeyError ):
		msg = "key error on 'username' or 'password''"
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = \
		{
			'status' : 'FAILURE',
			'msg'    : msg
		}

		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	user = auth.authenticate( username = username, password = password )
	if user is None:
		if settings.DEBUG == True:
			print >> stderr, "user:", "None"
		resp_dict = \
		{
			'status' : "FAILURE",
			'msg'    : "unrecognized user"
		}
		return HttpResponse( json.dumps( resp_dict ) )
	else:
		if settings.DEBUG == True:
			print >> stderr, "user_id:", user.id

	editglob = stopwords_get_editglob( username )
	if settings.DEBUG:
		print >> stderr, "editglob", editglob

	resp_dict = \
	{
		'status' : "SUCCESS",
		'editglob' : editglob
	}

	return HttpResponse( json.dumps( resp_dict ) )



@csrf_exempt
def stopwords_retrieve_table( request ):
	if settings.DEBUG == True: print >> stderr, "stopwords_retrieve_table()"

	req_dict = request.REQUEST		# searches POST first, then GET

	try:
		username = req_dict[ 'username' ]
		password = req_dict[ 'password' ]
	except( KeyError ):
		msg = "key error on 'username' or 'password''"
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = \
		{
			'status' : 'FAILURE',
			'msg'    : msg
		}

		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	user = auth.authenticate( username = username, password = password )
	if user is None:
		if settings.DEBUG == True:
			print >> stderr, "user:", "None"
		resp_dict = \
		{
			'status' : "FAILURE",
			'msg'    : "unrecognized user"
		}
		return HttpResponse( json.dumps( resp_dict ) )
#	else:
#		if settings.DEBUG == True:
#			print >> stderr, "user_id:", user.id

	try:
		# select_related(): follow the ForeignKey into the corpus table; 
		# when that data is needed, no additional queries are needed (fast!).
		sw_qset_all = StopWord.objects.select_related().all()
	#	print >> stderr, "all stopwords:", sw_qset_all.count()

		# all stopwords for this user
		sw_qset_user = sw_qset_all.filter( user = user )
	#	print >> stderr, "%s stopwords: %d" % ( username, sw_qset_user.count() )

		sw_qset_system = sw_qset_all.filter( user = None )
	#	print >> stderr, "system stopwords:", sw_qset_user.count()

		sw_qset = sw_qset_system | sw_qset_user
		sw_qset = sw_qset.order_by( 'id' )
	except:
		type, value, tb = exc_info()
		msg = "Stopwords could not be retrieved: %s" % value
		resp_dict = { 'status' : "FAILURE", 'msg' : msg }
		return HttpResponse( json.dumps( resp_dict ) )

	stoplist = []
	for sw in sw_qset:
	#	print >> stderr, sw.word, sw.query

		try:
			user = sw.user.username
		except:
			user = ""

		try:
			query = sw.query.title
		except:
			query = ""

		stopdict = \
		{
			"id"    : sw.id,
			"user"  : user,
			"query" : query,
			"word"  : sw.word
		}
		stoplist.append( stopdict )
#	print >> stderr, "stopwords:", stopwords

	stoplist = stoplist[ ::-1 ]
	resp_dict = \
	{
		'status'    : "SUCCESS",
		'editglob'  : stopwords_get_editglob( username ),
		'stopwords' : stoplist
	}
#	if settings.DEBUG == True:
#		print >> stderr, stoplist

	return HttpResponse( json.dumps( resp_dict ) )

# [eof]
