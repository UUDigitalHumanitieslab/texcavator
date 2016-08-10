# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from texcavator.utils import json_response_message, daterange2dates, flip_dict


def index(request):
    """Render main page."""

    from services.es import _KB_DISTRIBUTION_VALUES, _KB_ARTICLE_TYPE_VALUES
    config_reverse_mapping = {
        'sd': flip_dict(_KB_DISTRIBUTION_VALUES),
        'st': flip_dict(_KB_ARTICLE_TYPE_VALUES),
    }

    date_limits = daterange2dates(settings.TEXCAVATOR_DATE_RANGE)

    data = {
        "PROJECT_NAME": settings.PROJECT_NAME,
        "PROJECT_MIN_DATE": date_limits[0]['lower'],
        "PROJECT_MAX_DATE": date_limits[0]['upper'],
        "QUERY_DATA_DOWNLOAD_ALLOW": settings.QUERY_DATA_DOWNLOAD_ALLOW,
        "ES_INDEX": settings.ES_INDEX,
        "ES_REVERSE_MAPPING": json.dumps(config_reverse_mapping),
        "WORDCLOUD_MIN_WORDS": settings.WORDCLOUD_MIN_WORDS,
        "WORDCLOUD_MAX_WORDS": settings.WORDCLOUD_MAX_WORDS,
        "GUEST_MAX_RESULTS": settings.GUEST_MAX_RESULTS,
    }

    return render_to_response('index.html', data, RequestContext(request))


@csrf_exempt
def user_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    next_url = request.POST.get('next_url')

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)

            params = {
                "next_url": next_url
            }

            return json_response_message('SUCCESS', '', params)
        else:
            return json_response_message('ERROR', 'Account disabled.\n'
                                         'Please contact the system administrator.')
    else:
        return json_response_message('ERROR', 'The username or password you entered is invalid.')


@csrf_exempt
def guest_login(request):
    user = authenticate(username=settings.GUEST_USERNAME, password=settings.GUEST_PASSWORD)

    if user is not None:
        if user.is_active:
            login(request, user)

            params = {
                "username": user.username,
            }

            return json_response_message('SUCCESS', '', params)
        else:
            return json_response_message('ERROR', 'Account disabled.\n'
                                         'Please contact the system administrator.')
    else:
        return json_response_message('ERROR', 'The username or password you entered is invalid.')


@csrf_exempt
def user_logout(request):
    logout(request)

    return json_response_message('SUCCESS', '')
