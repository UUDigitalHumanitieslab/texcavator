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

from sys import stderr, exc_info
import requests
from itertools import chain

import logging
logger = logging.getLogger(__name__)

import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.html import escape
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from es import get_search_parameters, do_search, count_search_results, \
    single_document_word_cloud, multiple_document_word_cloud, get_document

from texcavator.utils import json_response_message
from services.celery import celery_check
from services.elasticsearch_biland import elasticsearch_htmlresp

from query.models import StopWord
from query.utils import get_query

from services.export import export_csv
from tasks import generate_tv_cloud


@login_required
def search(request):
    params = get_search_parameters(request.REQUEST)

    valid_q, result = do_search(settings.ES_INDEX,
                                settings.ES_DOCTYPE,
                                params['query'],
                                params['start']-1,  # Zero based counting
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


def request2extra4log(request):
    # pop conflicting keys
    #extra = request.META
    #extra.pop( "module", None )  # Attempt to overwrite 'module' in LogRecord
    # do we need to pop more?

    # minimum variant, can't do without 'REMOTE_ADDR' key
    try:
        remote_addr = request.META['REMOTE_ADDR']
    except:
        remote_addr = ""
    extra = {'REMOTE_ADDR': remote_addr}
    return extra


@csrf_exempt
@login_required
def doc_count(request):
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
        params = {'doc_count': str(doc_count)}
        return json_response_message('ok', 'Retrieved document count.', params)

    return json_response_message('error', 'Unable to retrieve document count'
                                 ' for query "{query}"' % query)


@csrf_exempt
@login_required
def cloud(request):
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
        return json_response_message('error', 'No word cloud generated.')

    ctype = 'application/json; charset=UTF-8'
    return HttpResponse(json.dumps(result), content_type=ctype)


@csrf_exempt
@login_required
def tv_cloud(request):
    """Generate termvector word cloud."""
    if settings.DEBUG:
        print >> stderr, "termvector cloud()"

    params = get_search_parameters(request.REQUEST)

    ids = request.REQUEST.get('ids')

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

    # Cloud by ids
    if ids:
        ids = ids.split(',')

        if len(ids) == 1:
            # Word cloud for single document
            t_vector = single_document_word_cloud(settings.ES_INDEX,
                                                  settings.ES_DOCTYPE,
                                                  ids[0],
                                                  min_length,
                                                  stopwords)

            ctype = 'application/json; charset=UTF-8'
            return HttpResponse(json.dumps(t_vector), content_type=ctype)

    # Cloud by queryID or multiple ids
    task = generate_tv_cloud.delay(params, min_length, stopwords, ids)

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


@login_required
def retrieve_document(request, doc_id):
    document = get_document(settings.ES_INDEX, settings.ES_DOCTYPE, doc_id)

    if document:
        return json_response_message('SUCCESS', '', document)
    return json_response_message('ERROR', 'Document not found.')


@csrf_exempt
def proxy(request):
    '''Proxy a request and return the result'''

    extra = request2extra4log(request)

    if settings.DEBUG:
        print >> stderr, "services/views.py/proxy()"

    logger.debug("services/views.py/proxy()", extra=extra)

    logger.debug("request.path_info: %s" % request.path_info, extra=extra)
    if settings.DEBUG:
        print >> stderr, "request.path_info:", request.path_info
        print >> stderr, "request.REQUEST:", request.REQUEST

    request_path = request.path_info.split('/')

    # Handle requests for specific services

    if len(request_path) > 2 and request_path[2] == u'logger' \
            and request.GET.has_key('message'):
        logger.debug(request.REQUEST['message'], extra=extra)
        return HttpResponse('OK')

    elif len(request_path) > 2 and request_path[2] == u'celery':
        if settings.DEBUG:
            print >> stderr, "Celery request\n"
        ctype = 'application/json; charset=UTF-8'
        return HttpResponse(celery_check(), content_type=ctype)

    elif len(request_path) > 3 and request_path[2] == u'scan':
        return download_scan_image(request)

    # If all fails, do a 404
    if settings.DEBUG:
        print >> stderr, "proxy: HttpResponseNotFound()"
    return HttpResponseNotFound()


@csrf_exempt
@login_required
def export_cloud(request):
    if settings.DEBUG:
        print >> stderr, "Export CSV request"
    return export_csv(request)


def download_scan_image(request):
    """download scan image file"""
    from django.core.servers.basehttp import FileWrapper
    import os

    if settings.DEBUG:
        print >> stderr, "download_scan_image()"

    req_dict = request.REQUEST
    _id = req_dict["id"]
    id_parts = _id.split('-')
    zipfile = req_dict["zipfile"]
    scandir = zipfile.split('_')[0]
    if settings.DEBUG:
        print >> stderr, _id, id_parts
        print >> stderr, zipfile, scandir

    # The filenames in the stabi dirs are not named in a consequent way.
    # Some contain the dir name, some not.
    # We added the dirname to the downsized jpegs if it was missing
    if _id.count('-') == 2:           # YYYY-MM-DD
        id4 = _id + '-'
        id4 += scandir
        filename = id4 + "_Seite_1.jpeg"
    else:
        # dirname = id_parts[ 3 ]
        id4 = _id
        filename = _id + "_Seite_1.jpeg"

    basedir = os.path.join(settings.STABI_IMG_DOWNLOAD, scandir, id4)

    pathname = os.path.join(settings.PROJECT_GRANNY, basedir, filename)

    if settings.DEBUG:
        print >> stderr, "basedir:  %s" % basedir
        print >> stderr, "filename: %s" % filename
        print >> stderr, "pathname: %s" % pathname

#   filename = "1863-07-01-9838247_Seite_1.png"
#   filename = "1872-01-17-9838247.pdf"

    if settings.DEBUG:
        print >> stderr, pathname

    wrapper = FileWrapper(open(pathname))
    # content_type = mimetypes.guess_type( pathname )[ 0 ]
    response = HttpResponse(wrapper, mimetype='content_type')
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


@login_required
def retrieve_kb_resolver(request):
    extra = request2extra4log(request)

    host = 'resolver.kb.nl'
    port = 80
    path = 'resolve'
    logger.debug('retrieve_kb_resolver: %s', request.META["QUERY_STRING"], extra=extra)

    kb_resolver_url = "http://" + host + ':' + str(port) + '/' + path + '?urn=' + request.REQUEST["id"]
    try:
        response = requests.get(kb_resolver_url)
    except:
        if settings.DEBUG:
            print >> stderr, "url: %s" % kb_resolver_url
        type, value, tb = exc_info()
        msg = "KB Resolver request failed: %s" % value.message
        if settings.DEBUG:
            print >> stderr, msg
        resp_dict = {"status": "FAILURE", "msg": msg}
        json_list = json.dumps(resp_dict)
        ctype = 'application/json; charset=UTF-8'
        return HttpResponse(json_list, content_type=ctype)

    resp_dict = \
        {
            "status": "SUCCESS",
            "text": response.content
        }

    json_list = json.dumps(resp_dict)
    ctype = 'application/json; charset=UTF-8'
    return HttpResponse(json_list, content_type=ctype)
