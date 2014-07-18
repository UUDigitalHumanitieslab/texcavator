"""Utility functions for the Texcavator app"""


import json
from django.http import HttpResponse


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def json_response_message(status, message, params=None):
    """Return HttpResponse object specifying a message to be send to the user
    interface.

    Parameters
    ----------
    status : string (ok|error)
    message : string explaining status
    params : dict containing additional parameters to include in the response

    Returns
    -------
    object: HttpResponse object containing status, message, and parameters 
        encoded as json object
    """
    response = {
        'status': status,
        'msg': message
    }

    if not params:
        params = {}

    for param, value in params.iteritems():
        response[param] = value

    return HttpResponse(json.dumps(response), 
                        'application/json; charset=UTF-8')
