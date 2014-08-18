# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.core import serializers

from django.conf import settings

from query.models import Query
from texcavator.utils import json_response_message


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
