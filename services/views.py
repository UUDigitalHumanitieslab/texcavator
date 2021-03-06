# -* coding: utf-8 -*-
"""Views for the services app
"""
import logging
from collections import Counter
from datetime import datetime
from sys import stderr

import requests
from celery.result import AsyncResult

from django.conf import settings
from django.http import JsonResponse
from django.utils.html import escape
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from es import get_search_parameters, do_search, count_search_results, \
    single_document_word_cloud, get_document, \
    metadata_aggregation, metadata_dict, articles_over_time, \
    get_stemmed_form

from texcavator.utils import json_response_message, daterange2dates, normalize_cloud

from query.models import Query, StopWord, Newspaper

from services.export import export_csv
from services.tasks import generate_tv_cloud

logger = logging.getLogger(__name__)


@login_required
def search(request):
    """Perform search request and return html string with results"""

    logger.info('services/search/ - user: {}'.format(request.user.username))

    params = get_search_parameters(request.GET)

    if not validate_dates(params['dates']):
        msg = 'You entered an invalid date range. Please check your date filters.'
        return json_response_message('error', msg)

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
        return json_response_message('ok', 'Search completed', {'hits': result['hits']})
    else:
        result = escape(result).replace('\n', '<br />')
        msg = 'Unable to parse query "{q}"<br /><br />'. \
            format(q=params['query'])
        msg = msg + result.replace('\n', '<br />')
        return json_response_message('error', msg)


def validate_dates(date_ranges):
    """
    Basic date validation: check if the entered date ranges are valid.
    TODO: also check for TEXCAVATOR_DATE_RANGE
    TODO: check if multiple date ranges do not conflict
    """
    for date_range in date_ranges:
        for date in date_range.values():
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return False
    return True


@csrf_exempt
@login_required
def doc_count(request):
    """
    Returns the number of documents returned by the current query
    """
    logger.info('services/doc_count/ - user: {}'.format(request.user.username))

    if settings.DEBUG:
        print >> stderr, "doc_count()"

    params = get_search_parameters(request.GET)

    result = count_search_results(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  params['query'],
                                  params['dates'],
                                  params['distributions'],
                                  params['article_types'],
                                  params['pillars'])

    count = result.get('count', None)

    if count:
        params = {'doc_count': count}
        logger.info('services/doc_count/ - returned calculated count.')
        return json_response_message('ok', 'Retrieved document count.', params)

    logger.info('services/doc_count/ - returned "unable to retrieve".')
    return json_response_message('error', 'Unable to retrieve document count')


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
def export_cloud(request):
    """Export cloud data to .csv file"""
    logger.info('services/export_cloud/')

    if settings.DEBUG:
        print >> stderr, "Export CSV request"
    return export_csv(request)


@login_required
def retrieve_kb_resolver(request, doc_id):
    logger.info('services/kb/resolver/')

    try:
        params = {
            'identifier': 'DDD:{}'.format(doc_id),
            'verb': 'GetRecord',
            'metadataPrefix': 'didl'}
        if settings.DEBUG:
            print >> stderr, 'url: {}, params: {}'.format(settings.KB_RESOLVER_URL, params)
        response = requests.get(settings.KB_RESOLVER_URL + settings.KB_API_KEY, params=params)
    except requests.exceptions.HTTPError as e:
        msg = 'KB Resolver request failed: {}'.format(str(e))
        if settings.DEBUG:
            print >> stderr, msg
        return json_response_message('error', msg)

    return json_response_message('success', 'Resolving successful', {'text': response.content})


@csrf_exempt
@login_required
def metadata(request):
    """This view will show metadata aggregations"""
    params = get_search_parameters(request.GET)
    result = metadata_aggregation(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  params['query'],
                                  params['dates'],
                                  params['distributions'],
                                  params['article_types'],
                                  params['pillars'],
                                  metadata_dict())

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


@csrf_exempt
@login_required
def heatmap(request, query_id, year):
    """
    Retrieves heatmap data for the given Query and year.
    """
    query = get_object_or_404(Query, pk=query_id)
    params = query.get_query_dict()

    year = int(year)
    range = daterange2dates(str(year - 5) + '0101,' + str(year + 5) + '1231')

    result = metadata_aggregation(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  params['query'],
                                  range,
                                  params['exclude_distributions'],
                                  params['exclude_article_types'],
                                  params['selected_pillars'],
                                  articles_over_time())

    articles_per_day = {}
    for bucket in result['aggregations']['articles_over_time']['buckets']:
        date = bucket['key'] / 1000  # Cal-HeatMap requires the date in seconds instead of milliseconds
        articles_per_day[date] = bucket['doc_count']

    return JsonResponse(articles_per_day)
