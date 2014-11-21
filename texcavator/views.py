# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from texcavator.utils import json_response_message
from services.es import daterange2dates

from texcavator.timestamp import TIMESTAMP


def index(request):
    """Render main page."""
    date_limits = daterange2dates('')
    dates = [date_limits['lower'], date_limits['upper']]
    daterange = [int(d.replace('-', '')) for d in dates]

    data = {
        "PROJECT_NAME": settings.PROJECT_NAME,

        "SRU_DATE_LIMITS": daterange,

        "QUERY_DATA_DOWNLOAD_ALLOW": settings.QUERY_DATA_DOWNLOAD_ALLOW,

        "ES_INDEX": settings.ES_INDEX,

        "ILPS_LOGGING": settings.ILPS_LOGGING
    }

    return render_to_response('index.html', data, RequestContext(request))


@csrf_exempt
def user_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)

            # TODO: are these datelimts really necessary?
            date_limits = daterange2dates('')
            dates = [date_limits['lower'], date_limits['upper']]
            daterange = [int(d.replace('-', '')) for d in dates]

            params = {
                "user_id": user.id,
                "user_name": user.username,
                "daterange": daterange,
                # TODO: what is timestamp used for? Is it really necessary
                "timestamp": TIMESTAMP
            }

            return json_response_message('SUCCESS', '', params)
        else:
            return json_response_message('ERROR', 'Account disabled.\n'
                                         'Please contact the system '
                                         'administrator.')

    return json_response_message('ERROR', 'Oops, that is not correct!')


@csrf_exempt
def user_logout(request):
    logout(request)

    return json_response_message('SUCCESS', '')
