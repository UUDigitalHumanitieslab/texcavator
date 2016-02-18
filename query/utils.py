"""Utility functions for saved queries."""

from sys import stderr

from django.conf import settings
from django.db import DatabaseError

from .models import Query
from services.es import get_document_ids, count_search_results
from texcavator.utils import json_response_message


def get_query_object(query_id):
    """
    Returns the query object stored for a query id and an appropriate error
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


def query2docidsdate(query, resolution):
    """
    Get the document ids plus their date for the query.
    """
    if settings.DEBUG:
        print >> stderr, "query2docidsdate()"

    query_dict = query.get_query_dict()

    return get_document_ids(settings.ES_INDEX,
                            settings.ES_DOCTYPE,
                            query_dict['query'],
                            query_dict['dates'],
                            resolution,
                            query_dict['exclude_distributions'],
                            query_dict['exclude_article_types'],
                            query_dict['selected_pillars'])


def count_results(query):
    """Returns the number of results for a Query"""
    params = query.get_query_dict()
    result = count_search_results(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  params['query'],
                                  params['dates'],
                                  params['exclude_distributions'],
                                  params['exclude_article_types'],
                                  params['selected_pillars'])
    return result.get('count')