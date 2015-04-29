"""Utility functions for the Texcavator app"""
from django.http import JsonResponse


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def json_response_message(status, message, params=None):
    """Return json object specifying a message to be send to the interface.
    This uses the `JSend <http://labs.omniti.com/labs/jsend>`_ format.

    Args:
        - status (str): (ok|error)
        - message (str): string explaining status
    Kwargs:
        - params (dict): dictionary containing additional parameters to include
          in the response

    Returns:
        HttpResponse object containing status, message, and
        parameters encoded as json object
    """
    response = {
        'status': status,
        'msg': message
    }

    if not params:
        params = {}

    # TODO: wrap this is in a 'data' entity to conform to JSend.
    for param, value in params.iteritems():
        response[param] = value

    return JsonResponse(response)
