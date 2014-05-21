"""Utility functions for the Texcavator app"""


import json
from django.http import HttpResponse


def json_error_message(message):
    """Return HttpResponse object specifying an error"""
    response = json.dumps({
        'status': 'error',
        'msg': message
    })

    return HttpResponse(response, 'application/json; charset=UTF-8')
