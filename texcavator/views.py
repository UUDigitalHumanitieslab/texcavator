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


@csrf_exempt
def loginajax( request ):

#	print >> stderr, "loginajax()"
#	print >> stderr, request.session

	req_dict = request.REQUEST		# searches POST first, then GET

	try:
		username    = req_dict[ "username" ]
		password    = req_dict[ "password" ]
		projectname = req_dict[ "projectname" ]
	#	print >> stderr, "username: %s" % username
	#	print >> stderr, "password: %s" % password
	#	print >> stderr, "projectname: %s" % projectname
	except( KeyError ):
		msg = "loging failed: key error"
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = { 'status' : 'FAILURE', 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )
	#	return HttpResponse( "false" )

#	redirect_to = request.REQUEST.get( REDIRECT_FIELD_NAME, '' )

	try:
		user = auth.authenticate( username = username, password = password )
	except:
		# when a user password is created with Django-1.4 you 
		# will get an exception when subsequently using Django-1.3.1
		# apparently due to a change in the pwd generating mechanism
		# when a password is created
		if settings.DEBUG == True:
			print >> stderr, "authenticate exception"
		user = None

	if user is not None:
		date_limits = daterange2dates('')
		dates = [date_limits['lower'], date_limits['upper']]
		daterange = [int(d.replace('-', '')) for d in dates]

		msg = "Welcome %s" % username
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = \
		{
			"status"    : "ok", 
			"user_id"   : user.id,
			"user_name" : user.username,
			"msg"       : msg, 
			"daterange" : daterange,
			"timestamp" : TIMESTAMP
		}
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )
	else:
		msg = "Oops, that is not correct!"
		if settings.DEBUG == True:
			print >> stderr, msg
		# redirect...
		resp_dict = { 'status' : "FAIL", 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	"""
	if not errors:
		if not redirect_to or '://' in redirect_to or ' ' in redirect_to:
			redirect_to = '/accounts/profile/'

		request.session[ SESSION_KEY ] = manipulator.get_user_id()
		request.session.delete_test_cookie()
		return HttpResponse( redirect_to )
	else:
		return HttpResponse( "false" )
	"""

# [eof]
