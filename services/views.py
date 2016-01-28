# -* coding: utf-8 -*-
"""Views for the services app
"""
import logging
from collections import Counter
from sys import stderr, exc_info

import requests
from celery.result import AsyncResult

from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from es import get_search_parameters, do_search, count_search_results, \
    single_document_word_cloud, get_document, \
    metadata_aggregation, get_stemmed_form

from texcavator.utils import json_response_message, daterange2dates, normalize_cloud

from query.models import Query, StopWord, Newspaper
from query.utils import get_query_object

from services.export import export_csv
from services.tasks import generate_tv_cloud
from services.elasticsearch_biland import elasticsearch_htmlresp

logger = logging.getLogger(__name__)


@login_required
def search(request):
    """Perform search request and return html string with results"""

    logger.info('services/search/ - user: {}'.format(request.user.username))

    params = get_search_parameters(request.REQUEST)

    valid_q, result = do_search(settings.ES_INDEX,
                                settings.ES_DOCTYPE,
                                params['query'],
                                params['start']-1,  # Zero based counting
                                params['result_size'],
                                params['dates'],
                                params['distributions'],
                                params['article_types'],
                                params['pillars'],
                                sort_order=params['sort_order'])
    if valid_q:
        html_str = elasticsearch_htmlresp(settings.ES_INDEX,
                                          params['start'],
                                          params['result_size'],
                                          result)
        return json_response_message('ok', 'Search completed', {'html': html_str})
    else:
        result = escape(result).replace('\n', '<br />')
        msg = 'Unable to parse query "{q}"<br /><br />'. \
            format(q=params['query'])
        msg = msg + result.replace('\n', '<br />')
        return json_response_message('error', msg)


@csrf_exempt
@login_required
def doc_count(request):
    """Returns the number of documents returned by a query
    """
    logger.info('services/doc_count/ - user: {}'.format(request.user.username))

    if settings.DEBUG:
        print >> stderr, "doc_count()"

    query_id = request.REQUEST.get('queryID')
    logger.info('services/doc_count/ - queryID: {}'.format(query_id))

    if query_id:
        query, response = get_query_object(query_id)

        if not query:
            logger.info('services/doc_count/ - returned cached response.')
            return response
    else:
        logger.info('services/doc_count/ - returned "missing query id".')
        return json_response_message('error', 'Missing query id.')

    params = query.get_query_dict()
    logger.info('services/doc_count/ - params: {}'.format(params))

    result = count_search_results(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  params['query'],
                                  params['dates'],
                                  params['exclude_distributions'],
                                  params['exclude_article_types'],
                                  params['selected_pillars'])
    logger.info('services/doc_count/ - ES returned normally')

    count = result.get('count', 'error')

    if not count == 'error':
        params = {'doc_count': str(count)}
        logger.info('services/doc_count/ - returned calculated count.')
        return json_response_message('ok', 'Retrieved document count.', params)

    logger.info('services/doc_count/ - returned "unable to retrieve".')
    return json_response_message('error', 'Unable to retrieve document count'
                                 ' for query "{query}"' % query)


@csrf_exempt
@login_required
def tv_cloud(request):
    """Generate termvector word cloud using the termvector approach.

    Returns word cloud data for a single document word cloud (based on a single
    document id) and multiple document word clouds (either based on a list of
    document ids (i.e., timeline burst cloud) or a query with metadata).

    For multiple document word clouds, a celery task generates the cloud data.
    """
    if settings.DEBUG:
        print >> stderr, "termvector cloud()"
    logger.info('services/cloud/ - termvector word cloud')
    logger.info('services/cloud/ - user: {}'.format(request.user.username))

    # Retrieve the cloud settings
    query_id = request.GET.get('queryID')
    min_length = int(request.GET.get('min_length', 2))
    use_stopwords = request.GET.get('stopwords') == "1"
    use_default_stopwords = request.GET.get('stopwords_default') == "1"
    stems = request.GET.get('stems') == "1"

    # Retrieve the stopwords
    stopwords = []
    if use_stopwords:
        stopwords_user = list(StopWord.objects
                              .filter(user=request.user)
                              .filter(query=None)
                              .values_list('word', flat=True))

        stopwords_query = []
        if query_id:
            stopwords_query = list(StopWord.objects
                                   .filter(user=request.user)
                                   .filter(query__id=query_id)
                                   .values_list('word', flat=True))

        stopwords_default = []
        if use_default_stopwords:
            stopwords_default = list(StopWord.objects
                                     .filter(user=None)
                                     .filter(query=None)
                                     .values_list('word', flat=True))

        stopwords = stopwords_user + stopwords_query + stopwords_default

    record_id = request.GET.get('record_id')
    logger.info('services/cloud/ - record_id: {}'.format(record_id))

    idf_timeframe = request.GET.get('idf_timeframe')
    
    if record_id:
        # Cloud for a single document
        t_vector = single_document_word_cloud(settings.ES_INDEX,
                                              settings.ES_DOCTYPE,
                                              record_id,
                                              min_length,
                                              stopwords,
                                              stems)
        normalized = normalize_cloud(t_vector['result'], idf_timeframe)
        return json_response_message('ok', 'Word cloud generated', {'result': normalized})
    else:
        # Cloud for a query
        logger.info('services/cloud/ - multiple document word cloud')

        query = get_object_or_404(Query, pk=query_id)
        params = query.get_query_dict()

        # If we're creating a timeline cloud, set the min/max dates
        date_range = None
        if request.GET.get('is_timeline'):
            date_range = daterange2dates(request.GET.get('date_range'))

        task = generate_tv_cloud.delay(params, min_length, stopwords, date_range, stems, idf_timeframe)
        logger.info('services/cloud/ - Celery task id: {}'.format(task.id))

        return json_response_message('ok', '', {'task': task.id})


@login_required
def check_status_by_task_id(request, task_id):
    """
    Returns the status of the generate_tv_cloud task.
    If the task is finished, the results of the task are returned.
    """
    if not request.is_ajax():
        return json_response_message('ERROR', 'No access.')

    task = AsyncResult(task_id)

    try:
        if task.ready():
            if task.successful():
                return json_response_message('ok', '', task.get())
            else:
                return json_response_message('ERROR', 'Generating word cloud failed.')
        else:
            return json_response_message('WAITING', task.status, task.result)
    except AttributeError as e:
        return json_response_message('ERROR', 'Other error: {}'.format(str(e)))


def cancel_by_task_id(request, task_id):
    """Cancel Celery task.
    """
    logger.info('services/cancel_task/{}'.format(task_id))

    AsyncResult(task_id).revoke(terminate=True)

    return json_response_message('ok', '')


@login_required
def retrieve_document(request, doc_id):
    """Retrieve a document from the ES index"""
    logger.info('services/retrieve/{}'.format(doc_id))

    document = get_document(settings.ES_INDEX, settings.ES_DOCTYPE, doc_id)

    if document:
        return json_response_message('SUCCESS', '', document)
    return json_response_message('ERROR', 'Document not found.')


@csrf_exempt
@login_required
def log(request):
    """Log the request message to the logger"""
    logger.info('log')

    logger.debug(request.REQUEST['message'])
    return json_response_message('success', 'Message logged')


@csrf_exempt
@login_required
def export_cloud(request):
    """Export cloud data to cvs file"""
    logger.info('services/export_cloud/')

    if settings.DEBUG:
        print >> stderr, "Export CSV request"
    return export_csv(request)


@csrf_exempt
@login_required
def download_scan_image(request):
    """Download scan image file"""
    logger.info('download_scan_image')

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
    response = HttpResponse(wrapper, content_type='content_type')
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


@login_required
def retrieve_kb_resolver(request):
    logger.info('services/kb/resolver/')

    host = 'resolver.kb.nl'
    port = 80
    path = 'resolve'
    logger.debug('retrieve_kb_resolver: %s', request.META["QUERY_STRING"])

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
        return json_response_message('error', msg)

    return json_response_message('success', 'Resolving successful', {'text': response.content})


@csrf_exempt
@login_required
def metadata(request):
    """This view will show metadata aggregations"""
    # TODO: the current implementation depends upon correct settings in UI.
    # TODO: (cont) it's better to retrieve values from the saved query directly.
    params = get_search_parameters(request.REQUEST)
    result = metadata_aggregation(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  params['query'],
                                  params['dates'],
                                  params['distributions'],
                                  params['article_types'],
                                  params['pillars'])

    # Categorize newspaper_ids per Pillar
    pillars = Counter()
    for n in result['aggregations']['newspaper_ids']['buckets']:
        pillar = 'None'
        try:
            newspaper = Newspaper.objects.get(pk=n['key'])
        except Newspaper.DoesNotExist:
            # TODO: this means there's a paper_dc_identifier in ElasticSearch without a corresponding Newspaper.
            newspaper = None
        if newspaper and newspaper.pillar:
            pillar = newspaper.pillar.name
        pillars[pillar] += n['doc_count']

    # Mimic the result of the other aggregations
    result['aggregations']['pillar'] = [{'key': k, 'doc_count': v} for (k, v) in pillars.iteritems()]

    return json_response_message('success', 'Complete', result['aggregations'])


@csrf_exempt
@login_required
def stemmed_form(request):
    """Returns the stemmed form of a POSTed word"""
    word = request.POST.get('word')
    stemmed = get_stemmed_form(settings.ES_INDEX, word)
    return json_response_message('success', 'Complete', {'stemmed': stemmed})
