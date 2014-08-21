# -*- coding: utf-8 -*-
from sys import stderr
import datetime
import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core import serializers

from django.conf import settings

from query.models import Query, DayStatistic
from texcavator.utils import json_response_message
from query.utils import query2docidsdate


def index(request):
    """Return a list of queries for a given user."""
    # TODO: use Django's authentication system to set the user

    username = request.REQUEST.get('username')

    if username:
        lexicon_items = Query.objects.filter(user__username=username) \
                                     .order_by('-date_created')
    else:
        lexicon_items = Query.objects.none()

    params = {
        'lexicon_items': serializers.serialize('json', lexicon_items)
    }

    return json_response_message('OK', '', params)


def query(request, query_id):
    # TODO: check whether query belongs to the user

    query = get_object_or_404(Query, pk=query_id)

    params = {
        'query': query.get_query_dict()
    }

    return json_response_message('OK', '', params)


def timeline(request, query_id, collection = settings.ES_INDEX, resolution = 'year'):
	if settings.DEBUG == True:
		print >> stderr, "lexicon/bursts() query_id:", query_id, "resolution:", resolution

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

	li = get_object_or_404( Query, pk = query_id )

	# normalization and/or smoothing
	values = DayStatistic.objects.values( 'date', 'count' ).all()
	date2countC = {}
	for dc in values:
		if dc[ 'date' ] <= enddate and dc[ 'date' ] >= begindate:
			date2countC[ dc[ 'date' ] ] = dc[ 'count' ]

	date_begin = "%s-%s-%s" % ( begin[0:4], begin[4:6], begin[6:8] )    # YYYYMMDD -> YYYY-MM-DD
	date_end   = "%s-%s-%s" % (   end[0:4],   end[4:6],   end[6:8] )    # YYYYMMDD -> YYYY-MM-DD

	documents_raw = query2docidsdate( query_id, collection, date_begin, date_end )
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

	from query.burstsdetector import bursts

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
