# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Copyright:	Fons Laan, ILPS-ISLA, University of Amsterdam
Project		BILAND
Name:		views.py
Version:	0.24
Goal:		list/views definitions

def get_server_info( request )
def index( request )
def http404( request )
def http500( request )
def testpost( request )
def lexicon_metacount( lex_id )
def lexicon_ocrcount( lexicon_id )
def list_lexicon_docs( request, lex_id )
def list_lexicons( request )
def get_doc_tags( doc_id )
def list_lexicon( request, lex_id )
def list_lexicon_words( request, lex_id )
def compare_lexicons( request, lex_id1, lex_id2 )

FL-10-Oct-2011: Created
FL-05-Jul-2013: Changed
"""

from sys import exit, stderr, exc_info
import requests

try:
	import json						# Python-2.6+
except:
	import django.utils.simplejson as json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from lexicon.models import LexiconItem


def get_server_info( request ):
	meta = request.META
	port = int( meta[ "SERVER_PORT" ] )
#	print >> stderr, "server port: %s" % request.META[ "SERVER_PORT" ]

	if port == settings.DEV_SERVER_PORT:
		scheme_authority = "http://localhost:" + str( port )
		sub_site = "/"
	else:
		scheme_authority = "http://" + settings.HOSTNAME + ":" + str( port )
		sub_site = settings.SUB_SITE

	return scheme_authority, sub_site



def index( request ):
	"""\
	Presents initial html page
	"""

	scheme_authority, sub_site = get_server_info( request )
#	print >> stderr, "scheme_authority: %s" % scheme_authority
#	print >> stderr, "SUB_SITE: %s" % sub_sit 

	"""
	meta = request.META
	referrer = meta[ "HTTP_REFERER" ]
	if referrer != "":
		static_prefix = scheme_authority
	else:
		static_prefix = ''
	"""

	template = "list/index.html"
	dictionary = { 'SUB_SITE' : sub_site }

	# context contains csrf_token (and STATIC_URL for django >= 1.3)
	context = RequestContext( request )

	return render_to_response( template, dictionary, context )



def http404( request ):
	"""\
	test template
	"""
	scheme_authority, sub_site = get_server_info( request )
	template = "404.html"
	dictionary = { }
	context = RequestContext( request )

	return render_to_response( template, dictionary, context )



def http500( request ):
	"""\
	test template
	"""
	scheme_authority, sub_site = get_server_info( request )
	template = "500.html"
	dictionary = { }
	context = RequestContext( request )

	return render_to_response( template, dictionary, context )



@csrf_exempt
def testpost( request ):
	"""\
	testpost
	"""
	print >> stderr, "testpost()"
	method = request.method
	path_info = request.path_info
	if method == 'GET':
		print >> stderr, "GET"
	elif method == 'POST':
		print >> stderr, "POST"

	req_dict = request.REQUEST
	print >> stderr, req_dict

	try:
		id = req_dict[ "id" ]
	except:
		id = ''

	try:
		key = req_dict[ "key" ]
	except:
		key = ''

	scheme_authority, sub_site = get_server_info( request )
	template = "list/testpost.html"
	dictionary = \
	{
		'method'    : method,
		'path_info' : path_info,
		'req_dict'  : req_dict,
		'id'        : id,
		'key'       : key
	}
	context = RequestContext( request )

#	return HttpResponse( status = 201 )
	return render_to_response( template, dictionary, context )



def lexicon_metacount( lex_id ):
	metadata_count = 0

	try:
		lexicon = LexiconItem.objects.get( pk = lex_id )
	except:
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "error: %s" % value.message

		if value.message == "<class 'lexicon.models.DoesNotExist'>":
			return metadata_count
		else:
			dictionary = \
			{
				"status"   : "ERROR",
				"message"  : err_msg
			}
			return HttpResponse( json.dumps( dictionary ), mimetype = "application/json" )

	try:
		metadata_count = lexicon.documents.count()
		if settings.DEBUG == True:
			print >> stderr, "metadata count: %d" % metadata_count
	except:
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "error: %s" % value.message
		dictionary = \
		{
			"status"   : "ERROR",
			"message"  : value.message
		}
		return HttpResponse( json.dumps( dictionary ), mimetype = "application/json" )

	return metadata_count



def lexicon_ocrcount( lexicon_id ):
	"""\
	lexicon xTAS ocr_data count
	"""
#	print >> stderr, "list_lexicon_ocrdocs()"

	if len( settings.XTAS_PREFIX ) > 0:
		xtas_url = "http://" + XTAS_HOST + ':' + str( settings.XTAS_PORT ) + '/' + settings.XTAS_PREFIX + "/doc"
	else:
		xtas_url = "http://" + XTAS_HOST + ':' + settings.XTAS_PORT + "/doc"
#	print >> stderr, xtas_url

	# get article data from xTAS
	lexicon_tag = "Lexicon" + str( lexicon_id )
	params = { 'key' : settings.XTAS_API_KEY, 'tags' : lexicon_tag }

	try:
		response = requests.get( xtas_url, params = params )
		content = response.content
	except:
		if settings.DEBUG == True:
			print >> stderr, "url: %s" % xtas_url
			print >> stderr, "params: %s" % params
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "xTAS request failed: %s" % value.message
		content = ""
		article_count = 0

	if content == "404 No documents found":
		article_count = 0
	else:
		try:
		#	print >> stderr, response.content
			jsdata = json.loads( response.content )
		#	print >> stderr, jsdata
			status = jsdata[ "status" ]
			if status == "error":
				article_count = 0
			else:
				article_count = jsdata[ "result" ][ "count" ]
		except:
			article_count = 0
	return article_count



def list_lexicon_docs( request, lex_id ):
	"""\
	lexicon meta_data & ocr_data counts
	"""
#	print >> stderr, "list_lexicon_docs()"

	metadata_count = lexicon_metacount( lex_id )
	ocrdata_count  = lexicon_ocrcount( lex_id )

	dictionary = \
	{
		"status"   : "SUCCESS",
		"message"  : "",
		"metadata" : metadata_count,
		"ocrdata"  : ocrdata_count
	}

	return HttpResponse( json.dumps( dictionary ), mimetype = "application/json" )



def list_lexicons( request ):
	"""\
	Show overview of lexicons, and stored article counts
	"""
	if settings.DEBUG == True:
		print >> stderr, "list_lexicons()"

	req_dict = request.REQUEST		# searches POST first, then GET
	try:
		user = req_dict[ 'user' ]
	except( KeyError ):
		user = None

	# select_related(): follow the ForeignKey into the corpus table; 
	# when that data is needed, no additional queries are needed (fast!). 
	if user:
		lexicons_qset = LexiconItem.objects.select_related().filter( user = user )
	else:
		lexicons_qset = LexiconItem.objects.select_related().all()
	nlexicons = lexicons_qset.count()		# instead of len(), when we do not need all hits to be retrieved
	if settings.DEBUG == True:
		print >> stderr, "nlexicons: %d" % nlexicons
	message = "%d lexicons" % nlexicons

	nums = []
	lexicon_ids = []
	lexicon_titles = []
	lexicon_users = []
	lexicon_groups = []
	metadata_counts = []
	article_counts = []

	if nlexicons == 0:
		lists_data = None

	for l in range( nlexicons ):
		# get metadata from django
		lexicon = lexicons_qset[ l ]
		lexicon_id = lexicon.id
		metadata_count = lexicon.documents.count()

		nums.append( l+1 )
		lexicon_ids.append( lexicon_id )
		lexicon_titles.append( lexicon.title )
		lexicon_users.append( lexicon.user )
		lexicon_groups.append( lexicon.group )
		metadata_counts.append( metadata_count )

		article_count = lexicon_ocrcount( lexicon_id )
		article_counts.append( article_count )

		if settings.DEBUG == True:
			print >> stderr, "# %d, id: %d, metadata: %d, ocrdata: %d, title: %s" % \
				( l+1, lexicon_id, metadata_count, article_count, lexicon.title.encode( 'utf-8' ) )

		lists_data = zip( nums, lexicon_ids, lexicon_titles, lexicon_users, lexicon_groups, metadata_counts, article_counts )

	scheme_authority, sub_site = get_server_info( request )
	dictionary = \
	{
		'SUB_SITE'      : sub_site,
		'STATIC_PREFIX' : scheme_authority,
		'STATIC_URL'    : settings.STATIC_URL,
		'message'       : message,
		'lists_data'    : lists_data
	}

	template = "list/lexicons.html"
	context = RequestContext( request )

	return render_to_response( template, dictionary, context )



def get_doc_tags( doc_id ):
	if len( settings.XTAS_PREFIX ) > 0:
		xtas_url = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT ) + '/' + settings.XTAS_PREFIX + "/doc"
	else:
		xtas_url = "http://" + settings.XTAS_HOST + ':' + settings.XTAS_PORT + "/doc"

	params = { 'key' : settings.XTAS_API_KEY, 'id' : doc_id }

	try:
		response = requests.get( xtas_url, params = params )
	except:
		if settings.DEBUG == True:
			print >> stderr, "url: %s" % xtas_url
			print >> stderr, "params: %s" % params
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "xTAS request failed: %s" % value.message
		article_count = 0

	content = response.content
#	print >> stderr, content
	doctaglist = []
	if content != "404 No documents found":
	#	print >> stderr, response.content
		jsdata = json.loads( response.content )
	#	print >> stderr, jsdata
		status = jsdata[ "status" ]
		if status == "ok":
			doctaglist = jsdata[ "result" ][ "document" ][ "tags" ]

#	doctaglist.sort()
	dog_tags = ",".join( doctaglist )

	return dog_tags



def list_lexicon( request, lex_id ):
	"""\
	List lexicon docid, compare metadata versus articles presence
	"""
	if settings.DEBUG == True:
		print >> stderr, "list_lexicon()"
		print >> stderr, "lex_id:", lex_id

	MAX_COUNT = 100

	if len( settings.XTAS_PREFIX ) > 0:
		xtas_url = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT ) + '/' + settings.XTAS_PREFIX + "/doc"
	else:
		xtas_url = "http://" + settings.XTAS_HOST + ':' + settings.XTAS_PORT + "/doc"
	if settings.DEBUG == True:
		print >> stderr, xtas_url

	# get metadata from django
	try:
		lexicon = LexiconItem.objects.get( pk = int(lex_id) )
		lexicon_title = lexicon.title
		metadata_count = lexicon.documents.count()
	except:
		lexicon_title = ''
		metadata_count = 0
		type, value, tb = exc_info()
		if value.message == "<class 'lexicon.models.DoesNotExist'>":
			pass	# no lexicon data for this lex_id
		else:
			if settings.DEBUG == True:
				print >> stderr, "django request failed: %s" % value.message

	nums_meta = []
	metadatas = []
	if metadata_count > 0:
		articles = lexicon.documents.all()
		for m in range( metadata_count ):
			article = articles[ m ]
			metadatas.append( article.identifier )
			nums_meta.append( m+1 )
	if settings.DEBUG == True:
		print >> stderr, "metadatas:", len( metadatas )

	# get article data from xTAS
	lexicon_tag = "Lexicon" + lex_id
	params = { 'key' : settings.XTAS_API_KEY, 'tags' : lexicon_tag }

	try:
		response = requests.get( xtas_url, params = params )
	except:
		if settings.DEBUG == True:
			print >> stderr, "url: %s" % xtas_url
			print >> stderr, "params: %s" % params
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "xTAS request failed: %s" % value.message
		article_count = 0

	content  = response.content
	if content == "404 No documents found":
		article_count = 0
	else:
	#	print >> stderr, response.content
		jsdata = json.loads( response.content )
	#	print >> stderr, jsdata
		status = jsdata[ "status" ]
		if status == "error":
			article_count = 0
		else:
			article_count = jsdata[ "result" ][ "count" ]

	if settings.DEBUG == True:
		print >> stderr, "articles", article_count


	articles = []
	articles_tags = []
	if article_count > 0:
	#	print >> stderr, jsdata
		docs = jsdata[ "result" ][ "ids" ]
		for doc_id in docs:
		#	print >> stderr, doc_id
			articles.append( doc_id )
			params = { 'key' : settings.XTAS_API_KEY, 'id' : doc_id }

			try:
				response = requests.get( xtas_url, params = params )
			except:
				if settings.DEBUG == True:
					print >> stderr, "url: %s" % xtas_url
					print >> stderr, "params: %s" % params
				type, value, tb = exc_info()
				if settings.DEBUG == True:
					print >> stderr, "xTAS request failed: %s" % value.message
				article_count = 0

		#	print >> stderr, response.content
			jsdata = json.loads( response.content )
		#	print >> stderr, jsdata
			status = jsdata[ "status" ]

			if status == "ok":
				doctaglist = jsdata[ "result" ][ "document" ][ "tags" ]
				dog_tags = ",".join( doctaglist )
			else:
				dog_tags = ""

		#	print >> stderr, "dog_tags: |%s|" % dog_tags
			articles_tags.append( dog_tags )
		#	print >> stderr, "docid: %s, tags: %s" % ( doc_id, dog_tags )


	# from heapq import merge		# python 2.6+
	# list( merge( list1, list2 ) )
	docs = sorted( metadatas + articles )
	docs = list( set( docs ) )		# remove duplicates
	num_docs = len( docs )
	show_count = min( num_docs, MAX_COUNT )

	# mark in which list(s) the doc are
	nums = []
	in_meta = []
	in_arts = []
	art_tags = []
	art_tag_count = 0

	for d in range( show_count ):
		doc = docs[ d ]
		nums.append( d+1 )
		try:
			metadatas.index( doc )
			in_meta.append( '+' )
		except:
			in_meta.append( '-' )

		try:
			articles.index( doc )
			in_arts.append( '+' )
			art_tags.append( articles_tags[ art_tag_count ] )
			art_tag_count += 1
		except:
			in_arts.append( '-' )
			art_tags.append( '' )

	lists_data = zip( nums, in_meta, in_arts, docs, art_tags )

	scheme_authority, sub_site = get_server_info( request )
	dictionary = \
	{
		'SUB_SITE'       : sub_site,
		'STATIC_PREFIX'  : scheme_authority,
		'STATIC_URL'     : settings.STATIC_URL,
		'lexicon_tag'    : lexicon_tag,
		'lexicon_title'  : lexicon_title,
		'metadata_count' : metadata_count,
		'article_count'  : article_count,
		'show_count'     : show_count,
		'lists_data'     : lists_data
	}
	template = "list/lexicon.html"
	context = RequestContext( request )

	return render_to_response( template, dictionary, context )



def list_lexicon_words( request, lex_id ):
	"""\
	List lexicon word frequecies
	"""
	if settings.DEBUG == True:
		print >> stderr, "list_lexicon_words()"
		print >> stderr, "lex_id:", lex_id

#	MAX_WORDS = 100
	MAX_WORDS = 200
#	MAX_WORDS = 3000

	lexicon_tag = "Lexicon" + lex_id

	# get metadata from django
	try:
		lexicon = LexiconItem.objects.get( pk = int(lex_id) )
		lexicon_title = lexicon.title
		metadata_count = lexicon.documents.count()
	except:
		lexicon_title = ''
		metadata_count = 0
		type, value, tb = exc_info()
		if value.message == "<class 'lexicon.models.DoesNotExist'>":
			pass	# no lexicon data for this lex_id
		else:
			if settings.DEBUG == True:
				print >> stderr, "django request failed: %s" % value.message

	if settings.DEBUG == True:
		print >> stderr, "lexicon:", lexicon_tag
		print >> stderr, "title:", lexicon_title

	path = "/cloud"
	if len( settings.XTAS_PREFIX ) > 0:
		xtas_url = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT ) + '/' + settings.XTAS_PREFIX + path
	else:
		xtas_url = "http://" + settings.XTAS_HOST + ':' + settings.XTAS_PORT + path
	if settings.DEBUG == True:
		print >> stderr, xtas_url

	# get article data from xTAS
	xtas_filter = "apos,quot,0,1,2,3,4,5,6,7,8,9,10,11,000,_,__,den,de,in,ter,ten"
	lexicon_tag = "Lexicon" + lex_id
	params = \
	{
		'key'      : settings.XTAS_API_KEY,
		'tags'     : lexicon_tag,
		'words'    : 1,
		'stems'    : 0,					# { 0 | 1 } stemming
		'stopwords': 1,					# { 0 | 1 } exclude stopwords
		'order'    : "count",			# { "count" | "alpha" }, default is "alpha"
		'exclude'  : xtas_filter		# stopword csv string
	}
	#	'output'   : "xml"				# { "xml" | "json" }	new xTAS API always returns JSON
	if settings.DEBUG == True:
		print >> stderr, params

	try:
		response = requests.get( xtas_url, params = params )
	except:
		if settings.DEBUG == True:
			print >> stderr, "url: %s" % xtas_url
			print >> stderr, "params: %s" % params
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "xTAS request failed: %s" % value.message
		root = None
	else:
		if settings.DEBUG == True:
			print >> stderr, "status_code:", response.status_code
			print >> stderr, "response:", response.content
		jsdata = json.loads( response.content )
		if settings.DEBUG == True:
			print >> stderr, jsdata
		status = jsdata[ "status" ]
		if status == "error":
			terms = []
		elif status == "processing":
			taskid = jsdata[ "taskid" ]
			if settings.DEBUG == True:
				print >> stderr, "processing, taskid: %s" % taskid
			terms = []
		else:
			terms = jsdata[ "result" ]


	term_list = []

	term_count = len( terms )
	length = min( term_count, MAX_WORDS )			# display only first MAX_WORDS terms
	# in the legacy API, the the word with the maximum count was given score 8.0; do we still need this?
	if settings.DEBUG == True:
		print >> stderr, terms[ 0 ]
	maxcount = terms[ 0 ][ "count" ]
	scorescale = 8.0 / float( maxcount )
	for t in range( length ):
		term = terms[ t ]
		word  = term[ "term" ]
		count = int( term[ "count" ] )
		score = "%1.6f" % (float( count ) * scorescale)		# legacy score had 6 decimal places
		if settings.DEBUG == True:
			print >> stderr, "%d: %s" % ( count, term )
		dict = { 'num' : t+1, 'word' : word, 'count' : count, 'score' : score }
		term_list.append( dict )

	if settings.DEBUG == True:
		print >> stderr, "term count: %d" % term_count

	# sorting >= Python-2.6
#	sorted_list = sorted( term_list, key = itemgetter( 'count' ) )
	# sorting Python-2.5
#	sorted_list = sorted( term_list, key = lambda k: k[ 'count' ], reverse = True )
	# sorting now by Xtas
	sorted_list = term_list
	show_count = len( sorted_list )
#	print >> stderr, sorted_list

	nums   = []
	words  = []
	counts = []
	scores = []
	for d in range( len( sorted_list ) ):
		dict = sorted_list[ d ]
		num   = dict[ 'num' ]
		word  = dict[ 'word' ]
		count = dict[ 'count' ]
		score = dict[ 'score' ]

		nums.append( d+1 )
		words.append( word )
		counts.append( count )
		scores.append( score )

	#	print >> stderr, "word:", word, "count:", count, "score:", score

	lists_data = zip( nums, words, counts, scores )

	scheme_authority, sub_site = get_server_info( request )
	dictionary = \
	{
		'SUB_SITE'       : sub_site,
		'STATIC_PREFIX'  : scheme_authority,
		'STATIC_URL'     : settings.STATIC_URL,
		'lexicon_tag'    : lexicon_tag,
		'lexicon_title'  : lexicon_title,
		'term_count'     : term_count,
		'show_count'     : show_count,
		'lists_data'     : lists_data,
	}
	template = "list/wordcount.html"
	context = RequestContext( request )

	return render_to_response( template, dictionary, context )



def compare_lexicons( request, lex_id1, lex_id2 ):
	"""\
	Compare docids of 2 lexicons
	"""

	if settings.DEBUG == True:
		print >> stderr, "lex_id1", lex_id1
		print >> stderr, "lex_id2", lex_id2

	# get metadata from django for lex 1
	try:
		lexicon1 = LexiconItem.objects.get( pk = int( lex_id1 ) )
		lexicon1_title = lexicon1.title
		metadata_count1 = lexicon1.documents.count()
	except:
		lexicon1_title = ''
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "django request failed: %s" % value.message
		metadata_count1 = 0
	lexicon1_tag = "Lexicon" + lex_id1

	# get metadata from django for lex 2
	try:
		lexicon2 = LexiconItem.objects.get( pk = int( lex_id2 ) )
		lexicon2_title = lexicon2.title
		metadata_count2 = lexicon2.documents.count()
	except:
		lexicon2_title = ''
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "django request failed: %s" % value.message
		metadata_count2 = 0
	lexicon2_tag = "Lexicon" + lex_id2

#	print >> stderr, "metadata1", metadata_count1
#	print >> stderr, "metadata2", metadata_count2

	metadatas1 = []
	if metadata_count1 > 0:
		articles = lexicon1.documents.all()
		for article in articles:
			metadatas1.append( article.identifier )
	if settings.DEBUG == True:
		print >> stderr, "metadatas1:", len( metadatas1 )

	metadatas2 = []
	if metadata_count2 > 0:
		articles = lexicon2.documents.all()
		for article in articles:
			metadatas2.append( article.identifier )
	if settings.DEBUG == True:
		print >> stderr, "metadatas2:", len( metadatas2 )

	# from heapq import merge		# python 2.6+
	# list( merge( list1, list2 ) )
	metadatas = sorted( metadatas1 + metadatas2 )
	metadatas = list( set( metadatas ) )		# remove duplicates
	metadata_count = len( metadatas )

	if settings.DEBUG == True:
		print >> stderr, "metadatas:", len( metadatas )

	# mark in which list(s) the doc are
	nums = []
	in_1 = []
	in_2 = []
	both = []
	none = []
	
	for m in range( len( metadatas ) ):
		meta = metadatas[ m ]
		nums.append( m+1 )

		try:
			metadatas1.index( meta )
			is_in_1 = True
			in_1.append( '+' )
		except:
			is_in_1 = False
			in_1.append( '-' )

		try:
			metadatas2.index( meta )
			is_in_2 = True
			in_2.append( '+' )
		except:
			is_in_2 = False
			in_2.append( '-' )	

		if is_in_1 == True and is_in_2 == True:
			both.append( meta )
		if is_in_1 == False and is_in_2 == False:
			none.append( meta )

	both_count = len( both )
	none_count = len( none )
	if settings.DEBUG == True:
		print >> stderr, "both count", both_count
		for meta in both:
			print >> stderr, meta

		print >> stderr, "none count", none_count
		for meta in none:
			print >> stderr, meta

	lists_data = zip( nums, in_1, in_2, metadatas )

	scheme_authority, sub_site = get_server_info( request )
	dictionary = \
	{
		'SUB_SITE'       : sub_site,
		'STATIC_PREFIX'  : scheme_authority,
		'STATIC_URL'     : settings.STATIC_URL,
		'lexicon1_tag'   : lexicon1_tag,
		'lexicon1_title' : lexicon1_title,
		'lexicon1_count' : metadata_count1,
		'lexicon2_tag'   : lexicon2_tag,
		'lexicon2_title' : lexicon2_title,
		'lexicon2_count' : metadata_count2,
		'metadata_count' : metadata_count,
		'lists_data'     : lists_data
	}
	template = "list/compare.html"
	context = RequestContext( request )

	return render_to_response( template, dictionary, context )

# [eof]
