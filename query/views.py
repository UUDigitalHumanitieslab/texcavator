# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from django.conf import settings

from query.models import Query
from texcavator.utils import json_response_message


def query(request, query_id):
    # TODO: check whether query belongs to the user

    query = get_object_or_404(Query, pk=query_id)

    params = {
        'query': query.get_query_dict()
    }

    return json_response_message('OK', '', params)
