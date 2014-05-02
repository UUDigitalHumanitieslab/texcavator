# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		services/analytics.py
Version:	0.1
Goal:		dojox.analytics logging

FL-13-May-2013: Created
FL-26-Aug-2013: Changed
"""

from sys import stderr, exc_info
from datetime import date

import json

from django.conf import settings
from django.http import HttpResponse


def analytics( request ):
	if settings.DEBUG == True:
		print >> stderr, "analytics()"

	dict = request.REQUEST		# searches POST first, then GET

	try:
		_id = dict[ "id" ]
	except( KeyError ):
		_id = ""
	print >> stderr, "id: %s" % _id

	try:
		data = dict[ "data" ]
	except( KeyError ):
		data = ""
	print >> stderr, "data: %s" % data


	resp_dict =  { "status" : "ok", "msg" : "" }
	json_list = json.dumps( resp_dict )
	ctype = 'application/json; charset=UTF-8'
	return HttpResponse( json_list, content_type = ctype )


# [eof]
