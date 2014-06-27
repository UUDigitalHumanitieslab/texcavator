# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Copyright:  Daan Odijk, Fons Laan, ILPS-ISLA, University of Amsterdam
Project:    BiLand
Name:       services/views.py
Version:    0.35
Goal:       services/views

def request2extra4log( request )
def daterange2dates( dateRange_str )
def doc_count( request )
def cloud( request )
def proxy( request )
def download_scan_image( request )
def proxyResponse(method, host, port, path, data = {}, headers = {})
def buildResponse(response, content = '')
def applyXSLT( request, data, stylesheet )
def cql2es( request )

DO-%%-%%%-2011: Created
FL-07-Feb-2013: No more default daterange
FL-14-Feb-2013: Switch MongoDB / ElasticSearch
FL-13-May-2013: dojox.analytics
FL-06-Jun-2013: changed 'extra' for logging
FL-04-Jul-2013: -> BILAND app
FL-19-Dec-2013: Changed
"""

from sys import exit, stderr, exc_info
import httplib
import logging
import requests

import logging
logger = logging.getLogger( __name__ )

import json

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.http import urlencode
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt

from es import get_search_parameters, do_search, count_search_results, \
        single_document_word_cloud, multiple_document_word_cloud, \
        _KB_DISTRIBUTION_VALUES, _KB_ARTICLE_TYPE_VALUES

from texcavator.settings import TEXCAVATOR_DATE_RANGE
from texcavator.views import get_server_info
from texcavator.utils import json_response_message
from services.analytics import analytics
from services.celery import celery_check
from lexicon.models import LexiconItem
from lexicon.utils import get_query
from services.cql2es import callperl, cql2es_error
from services.elasticsearch_biland import es_doc_count, query2docids
from services.elasticsearch_biland import search_xtas_elasticsearch, retrieve_xtas_elasticsearch
from services.elasticsearch_biland import elasticsearch_htmlresp

from services.export import export_csv
from services.request import request2article_types, is_literal
from services.moses import moses

def search( request ):
    params = get_search_parameters(request.REQUEST)
    
    valid_q, result = do_search(settings.ES_INDEX_KONBIB,
                                settings.ES_INDEX_DOCTYPE_KONBIB,
                                params['query'],
                                params['start']-1, # Zero based counting
                                params['result_size'],
                                params['dates'],
                                params['distributions'],
                                params['article_types'])
    if valid_q:
        html_str = elasticsearch_htmlresp(settings.ES_INDEX_KONBIB, 
                                          params['start'], 
                                          params['result_size'],
                                          result)
        resp = {
                'status': 'ok',
                'html': html_str
               }
        return HttpResponse(json.dumps(resp), 
                            'application/json; charset=UTF-8')
    else:
        result = escape(result).replace('\n', '<br />')
        msg = 'Unable to parse query "{q}"<br /><br />'. \
            format(q=params['query'])
        msg = msg + result.replace('\n', '<br />')
        return json_response_message('error', msg)


def request2extra4log( request ):
    # pop conflicting keys
#   extra = request.META
#   extra.pop( "module", None )         # "Attempt to overwrite 'module' in LogRecord"
    # do we need to pop more?

    # minimum variant, can't do without 'REMOTE_ADDR' key
    try:
        remote_addr = request.META[ 'REMOTE_ADDR' ]
    except:
        remote_addr = ""
    extra = { 'REMOTE_ADDR' : remote_addr }
    return extra



@csrf_exempt
def doc_count( request ):
    if settings.DEBUG:
        print >> stderr, "doc_count()"
    
    lexiconID = request.REQUEST.get('lexiconID', None)

    query = None
    if lexiconID:
	    # get the query string from the Django db
        try:
            li = LexiconItem.objects.get(pk=lexiconID)
            query = li.query
        except LexiconItem.DoesNotExist:
            msg = "Lexicon with id %s cannot be found." % lexiconID
            logger.error( msg )
            if settings.DEBUG:
                print >> stderr, msg
            return json_response_message('error', msg)
        except DatabaseError:
            return json_response_message('error', 
                'Database error while retrieving lexicon')
    else:
        return json_response_message('error', 'Missing lexicon id.')

    if not query:
        return json_response_message('error', 'No query found.')
    
    params = get_search_parameters(request.REQUEST)
    
    result = count_search_results(params['collection'],
                                  settings.ES_DOCTYPE,
                                  query,
                                  params['dates'],
                                  params['distributions'],
                                  params['article_types'])

    doc_count = result.get('count', 'error')

    if not doc_count == 'error':
        params = {'doc_count' : str(doc_count)}
        return json_response_message('ok', 'Retrieved document count.', params)
    
    return json_response_message('error', 'Unable to retrieve document count' \
                              ' for query "{query}"' % query )


@csrf_exempt
def cloud( request ):
    if settings.DEBUG:
        print >> stderr, "cloud()"
    
    result = None

    params = get_search_parameters(request.REQUEST)
    
    ids = request.REQUEST.get('ids')
    
    # Cloud by ids
    if ids:
        ids = ids.split(',')

        if len(ids) == 1:
            # Word cloud for single document
            t_vector = single_document_word_cloud(settings.ES_INDEX, 
                                                  settings.ES_DOCTYPE,
                                                  ids[0])

            ctype = 'application/json; charset=UTF-8'
            return HttpResponse(json.dumps(t_vector), content_type = ctype)
        else:
            # Word cloud for multiple ids
            result = multiple_document_word_cloud(params.get('collection'), 
                                                  settings.ES_DOCTYPE, 
                                                  params.get('query'), 
                                                  params.get('dates'),
                                                  params.get('distributions'),
                                                  params.get('article_types'),
                                                  ids)

    # Cloud by lexiconID
    lexicon_id = request.REQUEST.get('lexiconID')

    if lexicon_id:
        query, response = get_query(lexicon_id)

        if not query:
            return response

        # for some reason, the collection to be searched is stored in parameter
        # 'collections' (with s added) instead of 'collection' as expected by 
        # get_search_parameters.
        coll = request.REQUEST.get('collections', settings.ES_INDEX)

        result = multiple_document_word_cloud(coll, 
                                              settings.ES_DOCTYPE, 
                                              query, 
                                              params.get('dates'),
                                              params.get('distributions'),
                                              params.get('article_types'))

    if not result:
        return json_response_message('error', 'No word cloud result generated.')
    
    ctype = 'application/json; charset=UTF-8'
    return HttpResponse(json.dumps(result), content_type = ctype)

    ##########################################################################
    # Old code starts here
    ##########################################################################

    # cloud by tags or docids

    extra = request2extra4log( request )

    req_dict = request.REQUEST
    if settings.DEBUG == True:
        print >> stderr, "req_dict:", req_dict

    # Django MergeDict -> normal dict (otherwise: cannot 'del') (see below)
    cloud_params = dict( req_dict )

    xtas_baseurl = "http://" + settings.XTAS_HOST + ':' + str( settings.XTAS_PORT )

    if len( settings.XTAS_PREFIX ) > 0:
        xtas_url = xtas_baseurl + '/' + settings.XTAS_PREFIX
    else:
        xtas_url = xtas_baseurl
    xtas_url = xtas_url + "/cloud"


    print >> stderr, "new cloud request"
    try:
        tags = req_dict[ "tags" ]       # cloud by tags
    except:
        tags = None

    try:
        ids = req_dict[ "ids" ]         # cloud by ids
    except:
        ids = None

    try:
        collection = req_dict[ "collections" ]

        if collection == settings.ES_INDEX_KONBIB:
            cloud_params[ "collections" ] = [ settings.ES_INDEX_KONBIB ]    # Ork expects collections, with s
        elif collection == settings.ES_INDEX_STABI:
            cloud_params[ "collections" ] = [ settings.ES_INDEX_STABI ]     # Ork expects collections, with s
        else:
            cloud_params[ "collections" ] = [ settings.ES_INDEX_KONBIB ]    # Ork expects collections, with s
    except:
        msg = "missing collection parameter";
        resp_dict =  { "status" : "error", "msg" : msg }
        json_list = json.dumps( resp_dict )
        ctype = 'application/json; charset=UTF-8'
        return HttpResponse( json_list, content_type = ctype )


    if tags is None and ids is None:    # cloud by lexiconID
        try:
            lexicon_id = req_dict[ "lexiconID" ]
        except:
            msg = "missing lexiconID parameter";
            resp_dict =  { "status" : "error", "msg" : msg }
            json_list = json.dumps( resp_dict )
            ctype = 'application/json; charset=UTF-8'
            return HttpResponse( json_list, content_type = ctype )

        try:
            dateRange = req_dict[ "dateRange" ]
        except:
            msg = "missing dateRange parameter";
            resp_dict =  { "status" : "error", "msg" : msg }
            json_list = json.dumps( resp_dict )
            ctype = 'application/json; charset=UTF-8'
            return HttpResponse( json_list, content_type = ctype )

        date_begin, date_end = daterange2dates( dateRange )

    #   status, msg, hits_total = es_doc_count( lexicon_id, collection, date_begin, date_end )
        status, msg, hits_total = es_doc_count( req_dict )
        if status != "ok":
            resp_dict =  { "status" : status, "error" : msg }
            json_list = json.dumps( resp_dict )
            ctype = 'application/json; charset=UTF-8'
            return HttpResponse( json_list, content_type = ctype )
        else:
            if hits_total > settings.XTAS_MAX_CLOUD_DOCS_ERROR:     # limit the number of cloud documents
                msg = "Too many documents for cloud.</br>The maximum number of cloud documents is currently set to " + str( settings.XTAS_MAX_CLOUD_DOCS_ERROR ) + ".";
                resp_dict =  { "status" : "error", "error" : msg }
                json_list = json.dumps( resp_dict )
                ctype = 'application/json; charset=UTF-8'
                return HttpResponse( json_list, content_type = ctype )

        doc_ids_list = query2docids( lexicon_id, collection, date_begin, date_end )
        doc_ids_str = ','.join( doc_ids_list )      # comma-separated string
        cloud_params[ "ids" ] = doc_ids_str         # add ids


    # remove non-cloud parameters
    if "datastore"   in cloud_params: del cloud_params[ "datastore" ]
#   if "collections" in cloud_params: del cloud_params[ "collections" ]
    if "lexiconID"   in cloud_params: del cloud_params[ "lexiconID" ]
    if "dateRange"   in cloud_params: del cloud_params[ "dateRange" ]

    cloud_params[ "key" ] = settings.XTAS_API_KEY   # add key
    if settings.DEBUG == True:
        print >> stderr, "xtas_url:", xtas_url
        print >> stderr, "params:", cloud_params

    try:
        response = requests.get( xtas_url, params = cloud_params )
    except:
        type, value, tb = exc_info()
        msg = "Cloud failed: %s" % value.message
        if settings.DEBUG == True:
            print >> stderr, msg
        logger.debug( "%s [%s]", title, msg, extra = extra )
        resp_dict = { 'status' : 'error', 'msg' : msg }
        json_list = json.dumps( resp_dict )
        ctype = 'application/json; charset=UTF-8'
        return HttpResponse( json_list, content_type = ctype )

    content = response.content

#   if settings.DEBUG == True:
#       print >> stderr, content
    ctype = 'application/json; charset=UTF-8'
    return HttpResponse( content, content_type = ctype )



@csrf_exempt
def proxy( request ):
    '''Proxy a request and return the result'''

    extra = request2extra4log( request )

    if settings.DEBUG == True:
        print >> stderr, "services/views.py/proxy()"

    logger.debug( "services/views.py/proxy()", extra = extra )

    logger.debug( "request.path_info: %s" % request.path_info, extra = extra )
    if settings.DEBUG == True:
        print >> stderr, "request.path_info:", request.path_info
        print >> stderr, "request.REQUEST:", request.REQUEST

    request_path = request.path_info.split('/')

    # Handle requests for specific services
    if len(request_path) > 2 and request_path[2] == u'analytics':
        if settings.DEBUG == True:
            print >> stderr, "Analytics request\n"
            return analytics( request)


    elif len(request_path) > 2 and request_path[2] == u'logger' and request.GET.has_key('message'):
        logger.debug( request.REQUEST['message'], extra = extra )
        return HttpResponse('OK')


    elif len(request_path) > 2 and request_path[2] == u'celery':
        if settings.DEBUG == True:
            print >> stderr, "Celery request\n"
        ctype = 'application/json; charset=UTF-8'
        return HttpResponse( celery_check(), content_type = ctype )


    elif len(request_path) > 2 and request_path[2] == u'export':
        if settings.DEBUG == True:
            print >> stderr, "Export CSV request\n"
        return export_csv( request )

    elif len(request_path) > 2 and request_path[2] == u'store':
        if settings.DEBUG == True:
            print >> stderr, "Store request", request.REQUEST

        datastore = request.REQUEST[ "datastore" ]
        if settings.DEBUG == True:
            print >> stderr, "datastore:", datastore

        if datastore == "DSTORE_MONGODB":
            return store_xtas_mongodb( request)             # xTAS MongoDB


    elif len(request_path) > 2 and request_path[2] == u'retrieve':
        if settings.DEBUG == True:
            print >> stderr, "Retrieve request", request.REQUEST

        datastore = request.REQUEST[ "datastore" ]
        if settings.DEBUG == True:
            print >> stderr, "datastore:", datastore

        if datastore == "DSTORE_ELASTICSEARCH":
            return retrieve_xtas_elasticsearch( request )       # elasticsearch.py
        elif datastore == "DSTORE_MONGODB":
            return retrieve_xtas_mongodb( request)              # xTAS MongoDB
        elif datastore == "DSTORE_KBRESOLVER":
            return retrieve_kb_resolver( request)               # KB Resolver
        else:
            msg = "Unknown datastore: %s" % datastore
            if settings.DEBUG == True:
                print >> stderr, msg
            resp_dict = { "status" : "FAILURE", "msg" : msg }
            json_list = json.dumps( resp_dict )
            ctype = 'application/json; charset=UTF-8'
            return HttpResponse( json_list, content_type = ctype )

    elif len( request_path ) > 3 and request_path[ 2 ] == u'scan':
        return download_scan_image( request )

    elif len( request_path ) > 3 and request_path[ 2 ] == u'moses':
        return moses( request )

    # If all fails, do a 404
    if settings.DEBUG == True:
        print >> stderr, "proxy: HttpResponseNotFound()"
    return HttpResponseNotFound()


def download_scan_image( request ):
    """download scan image file"""
    from django.core.servers.basehttp import FileWrapper
    import mimetypes
    import os

    if settings.DEBUG == True:
        print >> stderr, "download_scan_image()"

    req_dict = request.REQUEST
    _id = req_dict[ "id" ]
    id_parts = _id.split( '-' )
    zipfile = req_dict[ "zipfile" ]
    scandir = zipfile.split( '_' )[ 0 ]
    if settings.DEBUG == True:
        print >> stderr, _id, id_parts
        print >> stderr, zipfile, scandir

    # The filenames in the stabi dirs are not named in a consequent way. Some contain the dir name, some not. 
    # We added the dirname to the downsized jpegs if it was missing
    if _id.count( '-' ) == 2:           # YYYY-MM-DD
        id4 = _id + '-'
        id4 += scandir
        filename = id4 + "_Seite_1.jpeg"
    else:
        dirname = id_parts[ 3 ]
        id4 = _id
        filename = _id + "_Seite_1.jpeg"

    basedir = os.path.join( settings.STABI_IMG_DOWNLOAD, scandir, id4 )

#   pathname = os.path.join( settings.PROJECT_PARENT, basedir, filename )
    pathname = os.path.join( settings.PROJECT_GRANNY, basedir, filename )   # Django-1.5 extra dir level

    if settings.DEBUG == True:
        print >> stderr, "basedir:  %s" % basedir
        print >> stderr, "filename: %s" % filename
        print >> stderr, "pathname: %s" % pathname

#   filename = "1863-07-01-9838247_Seite_1.png"
#   filename = "1872-01-17-9838247.pdf"
#   pathname = os.path.join( settings.PROJECT_PARENT, "BILAND_download", filename )

    if settings.DEBUG == True:
        print >> stderr, pathname

    wrapper = FileWrapper( open( pathname ) )
    content_type = mimetypes.guess_type( pathname )[ 0 ]
    response = HttpResponse( wrapper, mimetype = 'content_type' )
#   response = HttpResponse( wrapper, content_type = 'application/pdf' )
    response[ 'Content-Disposition' ] = "attachment; filename=%s" % filename
    return response



def proxyResponse(method, host, port, path, data = {}, headers = {}):
    '''Proxy a request and return the result'''

    # Build a HTTP Connection to the host
    connection = httplib.HTTPConnection(host, port)
    
    if method == 'POST':
        # Set the correct header for the type of content we are sending
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        # Make the request
        connection.request(method, '/' + path, urlencode(data, True), headers)
    else:
        # Make a query based on the data to send
        query = ('?' + urlencode(data, True)) if len(data) else ''
        if settings.DEBUG == True:
            print >> stderr, "GET ", "host:", host, "\nport:", port, "\npath:", path, "\ndata:", data
            print >> stderr, "query:", query
        # Make the request
        connection.request(method, '/' + path + query)

    # Get the response for the request
    response = connection.getresponse()

    # Check if response is a redirect   
    if response.status == 301 or response.status == 302:
        from urlparse import urlparse
        # parse_qs was moved from cgi to urlparse, can use both
        try:
            from urlparse import parse_qs
        except ImportError:
            from cgi import parse_qs
        url = urlparse(response.getheader('Location'))
        # If the redirect uses the query string, mix it in with original data
        if(len(url.query)):
            data.update(parse_qs(url.query))
        # Do a new proxyResponse
        return proxyResponse(method, url.netloc, url.port, url.path, data, headers)

#   print >> stderr, "response status:", response.status

    return response



def buildResponse(response, content = ''):
    '''Build a Django HttpResponse, based on a httplib HTTPResponse.'''

    # if no content is given, try to read the response
    if len(content) == 0:
        content = response.read()
        
    # Get all headers from the httplib HTTPResponse
    responseHeaders = response.getheaders()
    # Make the Django HttpResponse, with the correct Content-Type
    httpResponse = HttpResponse(content, status=response.status, 
                                content_type=response.getheader('Content-Type'))
    
    # Add all headers from the response
    for header, value in responseHeaders:
        # Prevent adding of Hop-by-hop headers
        if header not in ['connection', 'transfer-encoding', 'content-length']:
            httpResponse[header] = value
    
    return httpResponse



def applyXSLT( request, data, stylesheet ):
    extra = request2extra4log( request )

    '''Apply a XSLT transformation from a XSLT file to XML data.'''
    # Use either lxml or libxml2 and libxslt

#   print >> stderr, "services/views.py/applyXSLT()"
#   print >> stderr, "input:\n", data

    try:
        from lxml import etree

    #   print >> stderr, "using lxml.etree"
    #   print >> stderr, "etree.parse"
        try:
            styledoc = etree.parse( stylesheet )
        #   print >> stderr, styledoc
        except:
            type, value, tb = exc_info()
            if settings.DEBUG == True:
                print >> stderr, "stylesheet could not be parsed: %s" % value
            logger.debug( "stylesheet could not be parsed: %s", value, extra = extra )

    #   print >> stderr, "etree.fromstring"
        doc = etree.fromstring( data )

    #   print >> stderr, "etree.XSLT"
        transform = etree.XSLT( styledoc )

        result = transform( doc )
    #   print >> stderr, "\noutput:\n", unicode(result)
    #   print >> stderr, "\noutput:\n", result.encode( 'utf-8' )    # 'lxml.etree._XSLTResultTree' object has no attribute 'encode'
    #   print >> stderr, "done"
        return unicode( result )

    except ImportError:
        import libxml2
        import libxslt

    #   print >> stderr, "using libxml2+libxslt"
        styledoc = libxml2.parseFile( stylesheet )
        style = libxslt.parseStylesheetDoc( styledoc )
        # Re-encode the document for compatibility
        doc = libxml2.parseDoc( data.decode( 'utf-8' ).encode( 'UTF-8' ) )
        result = style.applyStylesheet( doc, None )
        res = style.saveResultToString( result )
        style.freeStylesheet()
        doc.freeDoc()
        result.freeDoc()
    #   print >> stderr, "\noutput\n:\n", res
        return res



def test_cql2es( request ):
    """ Test whether cql2es returns a valid query.

    Now always returns {'status': 'ok'} (Function will be removed.)
    """
    if settings.DEBUG == True:
        print >> stderr, "cql2es()"

    query = request.REQUEST.get('query', None)
    
    if not query:
        resp_dict = { "status" : "error", "msg" : "Missing query" }
        json_list = json.dumps( resp_dict )
        ctype = 'application/json; charset=UTF-8'
        return HttpResponse( json_list, content_type = ctype )

    json_list = json.dumps({'status':'ok'})
    ctype = 'application/json; charset=UTF-8'
    return HttpResponse( json_list, content_type = ctype )


def retrieve_kb_resolver( request ):
	extra = request2extra4log( request )

	host = 'resolver.kb.nl'
	port = 80
	path = 'resolve'
	logger.debug( 'retrieve_kb_resolver: %s', request.META[ "QUERY_STRING" ], extra = extra )

	kb_resolver_url = "http://" + host + ':' + str( port ) + '/' + path + '?urn=' + request.REQUEST[ "id" ]
	try:
		response = requests.get( kb_resolver_url )
	except:
		if settings.DEBUG == True:
			print >> stderr, "url: %s" % kb_resolver_url
		type, value, tb = exc_info()
		msg = "KB Resolver request failed: %s" % value.message
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = { "status" : "FAILURE", "msg" : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	resp_dict = \
	{
		"status" : "SUCCESS",
		"text"   : response.content
	}

	json_list = json.dumps( resp_dict )
	ctype = 'application/json; charset=UTF-8'
	return HttpResponse( json_list, content_type = ctype )


# [eof]
