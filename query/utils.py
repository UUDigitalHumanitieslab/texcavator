"""Utility functions for saved queries."""

from sys import stderr

from django.conf import settings
from django.db import DatabaseError

from .models import Query
from services.es import get_document_ids
from texcavator.utils import json_response_message


def get_query_object(query_id):
    """Returns the query object stored for a query id and an appropriate error
    message if the query cannot be retrieved.
    """
    query = None
    response = None

    try:
        query = Query.objects.get(pk=query_id)
    except Query.DoesNotExist:
        msg = 'Query with id %s cannot be found.' % query_id
        response = json_response_message('error', msg)
    except DatabaseError:
        response = json_response_message(
            'error',
            'Database error while retrieving query.')

    if not query and not response:
        response = json_response_message('error', 'No query found.')

    return query, response


def query2docidsdate(query, date_begin, date_end):
    """Get the document ids plus their date for the query and date range.
    """
    # this is called multiple times by the timeline
    if settings.DEBUG:
        print >> stderr, "query2docidsdate()"

    date_range = {
        'lower': date_begin,
        'upper': date_end
    }

    return get_document_ids(settings.ES_INDEX, settings.ES_DOCTYPE, query.query, date_range)
