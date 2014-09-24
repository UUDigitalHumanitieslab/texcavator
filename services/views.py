# -* coding: utf-8 -*-

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
from itertools import chain

import logging
logger = logging.getLogger( __name__ )

import json

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.http import urlencode
from django.utils.html import escape
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from es import get_search_parameters, do_search, count_search_results, \
        single_document_word_cloud, multiple_document_word_cloud, \
        get_document_ids, termvector_word_cloud, _KB_DISTRIBUTION_VALUES, \
        _KB_ARTICLE_TYPE_VALUES

from texcavator.settings import TEXCAVATOR_DATE_RANGE
from texcavator.utils import json_response_message
from services.celery import celery_check
from lexicon.models import LexiconItem
from services.elasticsearch_biland import es_doc_count, query2docids
from services.elasticsearch_biland import search_xtas_elasticsearch, retrieve_xtas_elasticsearch
from services.elasticsearch_biland import elasticsearch_htmlresp

from query.models import Query, StopWord
from query.utils import get_query, get_query_object

from services.export import export_csv
from services.request import request2article_types, is_literal
from tasks import generate_tv_cloud

@login_required
def search( request ):
    params = get_search_parameters(request.REQUEST)
    
    valid_q, result = do_search(settings.ES_INDEX,
                                settings.ES_DOCTYPE,
                                params['query'],
                                params['start']-1, # Zero based counting
                                params['result_size'],
                                params['dates'],
                                params['distributions'],
                                params['article_types'])
    if valid_q:
        html_str = elasticsearch_htmlresp(settings.ES_INDEX, 
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
@login_required
def doc_count( request ):
    if settings.DEBUG:
        print >> stderr, "doc_count()"
    
    queryID = request.REQUEST.get('queryID')

    if queryID:
	    # get the query string from the Django db
        query, response = get_query(queryID)

        if not query:
            return response
    else:
        return json_response_message('error', 'Missing query id.')

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
@login_required
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

    # Cloud by queryID
    query_id = request.REQUEST.get('queryID')

    if query_id:
        query, response = get_query(query_id)

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


@csrf_exempt
@login_required
def tv_cloud(request):
    """Generate termvector word cloud."""
    if settings.DEBUG:
        print >> stderr, "termvector cloud()"

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
            return HttpResponse(json.dumps(t_vector), content_type=ctype)
        else:
            # Word cloud for multiple ids
            result = multiple_document_word_cloud(params.get('collection'),
                                                  settings.ES_DOCTYPE,
                                                  params.get('query'),
                                                  params.get('dates'),
                                                  params.get('distributions'),
                                                  params.get('article_types'),
                                                  ids)

    # Cloud by queryID
    query_id = request.GET.get('queryID')
    min_length = int(request.GET.get('min_length', 2))

    stopwords = []
    if request.GET.get('stopwords') == "1":
        stopwords_user = StopWord.objects.filter(user=request.user) \
                                         .filter(query=None)
        stopwords_query = StopWord.objects.filter(user=request.user) \
                                          .filter(query__id=query_id)

        stopwords = [stopw.word for stopw in list(chain(stopwords_user,
                                                        stopwords_query))]

    task = generate_tv_cloud.delay(params, min_length, stopwords)

    params = {'task': task.id}

    return json_response_message('ok', '', params)


@login_required
def check_status_by_task_id(request, task_id):
    """Returns the status of the generate_tv_cloud task. If the task is
    finished, the results of the task are returned.
    """
    if not request.is_ajax():
        return json_response_message('ERROR', 'No access.')

    # TODO: use generic AsyncResult (from celery.result import AsyncResult)
    # so this function can be used tu check the status of all asynchronous
    # tasks. However, when this import statement is put in this module, an
    # error is produced (celery module has no attribute result).
    # When typing this import statement in the Python
    # console or in the Django interactive shell, there is no error message.
    result = generate_tv_cloud.AsyncResult(task_id)

    try:
        if result.ready():
            if result.successful():
                return json_response_message('ok', '', result.get())
            else:
                return json_response_message('ERROR', 'Generating word cloud '
                                             'failed.')
        else:
            return json_response_message('WAITING', result.status)
    except AttributeError as e:
        return json_response_message('ERROR', 'Other error: {}'.format(str(e)))


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

    if len(request_path) > 2 and request_path[2] == u'logger' and request.GET.has_key('message'):
        logger.debug( request.REQUEST['message'], extra = extra )
        return HttpResponse('OK')


    elif len(request_path) > 2 and request_path[2] == u'celery':
        if settings.DEBUG == True:
            print >> stderr, "Celery request\n"
        ctype = 'application/json; charset=UTF-8'
        return HttpResponse( celery_check(), content_type = ctype )


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

    # If all fails, do a 404
    if settings.DEBUG == True:
        print >> stderr, "proxy: HttpResponseNotFound()"
    return HttpResponseNotFound()


@csrf_exempt
@login_required
def export_cloud(request):
    if settings.DEBUG == True:
        print >> stderr, "Export CSV request"
    return export_csv( request )


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


@login_required
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
