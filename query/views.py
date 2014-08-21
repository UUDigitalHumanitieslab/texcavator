# -*- coding: utf-8 -*-
from sys import stderr
from datetime import datetime
import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core import serializers

from django.conf import settings

from query.models import Query, DayStatistic
from texcavator.utils import json_response_message
from query.utils import query2docidsdate
from query.burstsdetector import bursts


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
