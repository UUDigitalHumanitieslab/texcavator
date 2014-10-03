# -*- coding: utf-8 -*-
from sys import stderr, exc_info
from datetime import datetime, date
import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

from django.conf import settings

from query.models import Distribution, ArticleType, Query, DayStatistic, \
                         StopWord
from texcavator.utils import json_response_message
from query.utils import query2docidsdate
from query.burstsdetector import bursts
from services.es import get_search_parameters

@login_required
def index(request):
    """Return a list of queries for a given user."""
    lexicon_items = Query.objects.filter(user=request.user) \
                                 .order_by('-date_created')

    params = {
        'lexicon_items': serializers.serialize('json', lexicon_items)
    }

    return json_response_message('OK', '', params)

@login_required
def query(request, query_id):
    query = get_object_or_404(Query, pk=query_id)
    if not request.user == query.user:
        return json_response_message('ERROR', 'Query does not belong to user.')

    params = {
        'query': query.get_query_dict()
    }

    return json_response_message('OK', '', params)


@csrf_exempt
@login_required
def create_query(request):
    params = get_search_parameters(request.POST)
    title = request.POST.get('title')
    comment = request.POST.get('comment')
    
    date_lower = datetime.strptime(params['dates']['lower'], '%Y-%m-%d')
    date_upper = datetime.strptime(params['dates']['upper'], '%Y-%m-%d')

    try:
        q = Query(query=params['query'],
                  title=title,
                  comment=comment,
                  user=request.user,
                  date_lower=date_lower, 
                  date_upper=date_upper)
        q.save()

        for distr in Distribution.objects.all():
            if distr.id in params['distributions']:
                q.exclude_distributions.add(distr)

        for art_type in ArticleType.objects.all():
            if art_type.id in params['article_types']:
                q.exclude_article_types.add(art_type)

    except Exception as e:
        return json_response_message('ERROR', str(e))

    return json_response_message('SUCCESS', '')


@csrf_exempt
@login_required
def delete(request, query_id):
    query = Query.objects.get(pk=query_id)
    if not query:
        return json_response_message('ERROR', 'Query not found.')

    if not request.user == query.user:
        return json_response_message('ERROR', 'Query does not belong to user.')

    q = query.query
    query.delete()

    return json_response_message('SUCCESS', 'Query "{}" deleted.'.format(q))


@csrf_exempt
@login_required
def update(request, query_id):
    query = Query.objects.get(pk=query_id)
    
    if not query:
        return json_response_message('ERROR', 'Query not found.')
    
    if not request.user == query.user:
        return json_response_message('ERROR', 'Query does not belong to user.')
    
    params = get_search_parameters(request.POST)
    title = request.POST.get('title')
    comment = request.POST.get('comment')
    
    date_lower = datetime.strptime(params['dates']['lower'], '%Y-%m-%d')
    date_upper = datetime.strptime(params['dates']['upper'], '%Y-%m-%d')

    try:
        Query.objects.filter(pk=query_id).update(query=params['query'],
                                                 title=title,
                                                 comment=comment,
                                                 date_lower=date_lower, 
                                                 date_upper=date_upper)

        query.exclude_distributions.clear()
        for distr in Distribution.objects.all():
            if distr.id in params['distributions']:
                query.exclude_distributions.add(distr)

        query.exclude_article_types.clear()
        for art_type in ArticleType.objects.all():
            if art_type.id in params['article_types']:
                query.exclude_article_types.add(art_type)

    except Exception as e:
        return json_response_message('ERROR', str(e))

    return json_response_message('SUCCESS', 'Query saved.')


@login_required
def timeline(request, query_id, resolution):
    if settings.DEBUG:
        print >> stderr, "query/bursts() query_id:", query_id, \
                         "resolution:", resolution

    collection = settings.ES_INDEX

    if request.REQUEST.get('normalize') == 1:
        normalize = True
    else:
        normalize = False

    bg_smooth = False

    begin = request.REQUEST.get('begindate')
    if not begin:
        return json_response_message('ERROR', 'No begin date specified.', None)

    end = request.REQUEST.get('enddate')
    if not end:
        return json_response_message('ERROR', 'No end date specified.', None)

    begindate = datetime.strptime(begin, '%Y%m%d').date()
    enddate = datetime.strptime(end, '%Y%m%d').date()

    get_object_or_404(Query, pk=query_id)

    # normalization and/or smoothing
    values = DayStatistic.objects.values('date', 'count').all()
    date2countC = {}
    for dc in values:
        if dc['date'] <= enddate and dc['date'] >= begindate:
            date2countC[dc['date']] = dc['count']

    documents_raw = query2docidsdate(query_id,
                                     collection,
                                     str(begindate),
                                     str(enddate))
    documents = sorted(documents_raw, key=lambda k: k["date"])
    doc2date = {}
    for doc in documents:
        doc_date = doc["date"]
        if doc_date <= enddate and doc_date >= begindate:
            doc2date[doc["identifier"]] = doc_date

    if settings.DEBUG:
        print >> stderr, "burst parameters:"
        # print >> stderr, "len doc2date:", len(doc2date)  # can be big
        print >> stderr, "(doc2date not shown)"
        print >> stderr, "doc2relevance: {}"
        # print >> stderr, "len date2countC:", len(date2countC)  # can be big
        print >> stderr, "(date2countC not shown)"
        print >> stderr, "normalize:", normalize
        print >> stderr, "bg_smooth:", False
        print >> stderr, "resolution:", resolution

    burstsList = bursts.bursts(doc2date,
                               {},
                               date2countC=date2countC,
                               normalise=normalize,
                               bg_smooth=bg_smooth,
                               resolution=resolution)[0]

    date2count = {}
    for date, tup in burstsList.iteritems():
        doc_float, zero_one, index, limit, doc_count, doc_ids = tup
        if doc_count != 0:
            doc_float = float("%.1f" % doc_float)  # less decimals
            if limit:                              # not None
                limit = float("%.1f" % limit)      # less decimals
            date2count[str(date)] = (doc_float,
                                     zero_one,
                                     index,
                                     limit,
                                     doc_count,
                                     doc_ids)

    return HttpResponse(json.dumps(date2count))


@csrf_exempt
@login_required
def add_stopword(request):
    query_id = request.POST.get('query_id')
    word = request.POST.get('stopword')

    q = None

    try:
        q = Query.objects.get(pk=query_id)
    except Query.DoesNotExist:
        pass
    except Exception as e:
        return json_response_message('ERROR', str(e))

    StopWord.objects.get_or_create(user=request.user, query=q, word=word)

    return json_response_message('SUCCESS', 'Stopword added.')


@csrf_exempt
@login_required
def delete_stopword(request, stopword_id):
    stopword = StopWord.objects.get(pk=stopword_id)
    if not stopword:
        return json_response_message('ERROR', 'Stopword not found.')

    if not request.user == stopword.user:
        return json_response_message('ERROR', 'Stopword does not belong to ' \
                                              'user.')
    stopword.delete()
    
    return json_response_message('SUCCESS', 'Stopword deleted.')


# TODO: turn into get method (get user via currently logged in user)
@csrf_exempt
@login_required
def stopwords(request):

    stopwords = StopWord.objects.select_related().filter(user=request.user) \
                                .order_by('word').order_by('query')

    stopwordlist = []
    for word in stopwords:
        stopwordlist.append(word.get_stopword_dict())

    params = {
        'stopwords': stopwordlist,
        'editglob': False
    }

    return json_response_message('SUCCESS', '', params)