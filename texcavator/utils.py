"""Utility functions for the Texcavator app"""
from datetime import datetime
from itertools import izip

from django.http import JsonResponse
from django.conf import settings


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def pairwise(iterable):
    """Iterates over every two elements, so s -> (s0,s1), (s2,s3), (s4, s5), ...
    Copied from: http://stackoverflow.com/a/5389547/3710392"""
    a = iter(iterable)
    return izip(a, a)


def daterange2dates(date_range_str):
    """Return a dictionary containing the date boundaries specified.

    If the input string does not specify two dates, the maximum date range is
    retrieved from the settings.
    """
    if not date_range_str:
        return daterange2dates(settings.TEXCAVATOR_DATE_RANGE)

    result = []
    dates = [str(datetime.strptime(d, '%Y%m%d').date()) for d in date_range_str.split(',')]
    for lower, upper in pairwise(dates):
        result.append({'lower': lower, 'upper': upper})

    return result


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
