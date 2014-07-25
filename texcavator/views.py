# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project		BiLand
Name:		views.py
Version:	0.23
Goal:		main views definitions

def getdaterange( projectname )
def horizon( request )
def loginajax( request )

FL-10-Oct-2011: Created
FL-04-Jul-2013: -> BILAND app
FL-06-Nov-2013: Changed
"""

from sys import stderr
import json

from django.conf import settings
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from texcavator.timestamp import TIMESTAMP


def getdaterange( projectname ): 
	project_name = projectname.lower()
	daterange = settings.SRU_DATE_LIMITS_KBALL

	if project_name == "wahsp":
		daterange = settings.SRU_DATE_LIMITS_WAHSP
	elif project_name == "biland":
		daterange = settings.SRU_DATE_LIMITS_BILAND
	elif project_name == "horizon":		# texcavator
		daterange = settings.SRU_DATE_LIMITS_HORIZON
	else:
		daterange = settings.SRU_DATE_LIMITS_KBALL

	return daterange



def index( request ):
	"""Returns settings used in JavaScript and displays the application web
    page.
	"""

	data = {
		"PROJECT_NAME": "Horizon",

		"CELERY_OWNER": settings.CELERY_OWNER,
		"SRU_DATE_LIMITS": settings.SRU_DATE_LIMITS_HORIZON,

		"XTAS_PREFIX": settings.XTAS_PREFIX,
		"XTAS_DATASTORE": settings.XTAS_DATASTORE,
		"XTAS_COLLECTION": settings.XTAS_COLLECTION,
		"XTAS_DOCS_SELECT": settings.XTAS_DOCS_SELECT,

		"XTAS_MAX_CLOUD_DOCS_WARN": settings.XTAS_MAX_CLOUD_DOCS_WARN,
		"XTAS_MAX_CLOUD_DOCS_ERROR": settings.XTAS_MAX_CLOUD_DOCS_ERROR,

		"QUERY_DATA_DOWNLOAD_ALLOW": settings.QUERY_DATA_DOWNLOAD_ALLOW,

		"ES_INDEX_KONBIB": settings.ES_INDEX_KONBIB,

		"ILPS_LOGGING": settings.ILPS_LOGGING
	}

	return render_to_response('index.html', data, RequestContext(request))


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
		daterange = getdaterange( projectname )

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
