# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project		BiLand
Name:		views.py
Version:	0.23
Goal:		main views definitions

def horizon( request )
def loginajax( request )

FL-10-Oct-2011: Created
FL-04-Jul-2013: -> BILAND app
FL-06-Nov-2013: Changed
"""

from sys import stderr
import json

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from texcavator.utils import json_response_message
from services.es import daterange2dates

from texcavator.timestamp import TIMESTAMP


def index( request ):
	"""Returns settings used in JavaScript and displays the application web
    page.
	"""
	date_limits = daterange2dates('')
	dates = [date_limits['lower'], date_limits['upper']]
	daterange = [int(d.replace('-', '')) for d in dates]

	data = {
		"PROJECT_NAME": "Horizon",

		"CELERY_OWNER": settings.CELERY_OWNER,
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
                "user_id"   : user.id,
                "user_name" : user.username,
                "daterange" : daterange,
                # TODO: what is timestamp used for? Is it really necessary
                "timestamp" : TIMESTAMP
            }

            return json_response_message('SUCCESS', '', params)
        else:
            return json_response_message('ERROR', 'Account disabled.\n' \
                                         'Please contact the system ' \
                                         'administrator.')

    return json_response_message('ERROR', 'Oops, that is not correct!' )
