"""Utility functions for saved queries."""


from django.db import DatabaseError

from models import Query


def get_query(query_id):
    """Returns the query stored for a query id and an appropriate error 
    message if the query cannot be retrieved.
    """
    query = None
    response = None

    try:
        qu = Query.objects.get(pk=query_id)
        query = qu.query
    except Query.DoesNotExist:
        msg = "Query with id %s cannot be found." % query_id
        response = json_response_message('error', msg)
    except DatabaseError:
        response = json_response_message('error', 
                'Database error while retrieving query.')

    if not query and not response: 
        response = json_response_message('error', 'No query found.')

    return query, response
