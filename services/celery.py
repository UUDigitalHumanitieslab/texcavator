# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		services/celery.py
Version:	0.2
Goal:		Celery check

FL-18-Dec-2012: Created
FL-26-Aug-2013:
"""

import os
from sys import stderr, exc_info
import subprocess

try:
	import json						# Python-2.6+
except:
	import django.utils.simplejson as json

from django.conf import settings


def celery_check():
	if settings.DEBUG == True:
		print >> stderr, "celery_check()"

	cmdline = "ps aux | grep celeryd"

	try:
		p = subprocess.Popen ( cmdline, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
	except:
		type, value, tb = exc_info()
		msg = "subprocess failed: %s" % value.message
		if settings.DEBUG == True:
			print >> stderr, msg

	resp_str = p.stdout.read()
	if settings.DEBUG == True:
		print >> stderr, os.environ[ "PATH" ]

	in_lines = resp_str.split( '\n' );
	out_lines = []
	for line in in_lines:
	#	print >> stderr, "line"
	#	print >> stderr, line
		if line.find( "manage.py celeryd" ) != -1:
			out_lines.append( line )

#	for line in out_lines:
#		print >> stderr, line

	dict = \
	{
		"status": "OK", 
		"data": out_lines
	}

	return json.dumps( dict )



if __name__ == '__main__':
	resp = celery_check()
	print >> stderr, resp

# [eof]
