# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		services/moses.py
Version:	0.1
Goal:		moses translation

def moses( request )

FL-18-Jun-2013: Created
FL-26-Aug-2013: Changed
"""

import os
import subprocess
import tempfile
from sys import stderr, exc_info

import logging
logger = logging.getLogger( __name__ )

try:
	import json						# Python-2.6+
except:
	import django.utils.simplejson as json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger( 'BILAND.services' )

def execute( text ):
#	$ cd $MOSES_DECODER/sample-models
#	$ $MOSES_HOME/bin/moses -f phrase-model/moses.ini < phrase-model/in > out
	if settings.DEBUG == True:
		print >> stderr, "MOSES_HOME:", settings.MOSES_HOME
		print >> stderr, "MOSES_DECODER:", settings.MOSES_DECODER

#	in_temp = tempfile.NamedTemporaryFile()
	in_tempname = "/tmp/moses_in"
#	in_tempname = os.path.join( settings.MOSES_DECODER, "in_moses" )

#	out_temp = tempfile.NamedTemporaryFile()
	out_tempname = "/tmp/moses_out"
#	out_tempname = os.path.join( settings.MOSES_DECODER, "out_moses" )

#	text = "das ist ein kleines haus\ndie ist ein langes mauer\n"
	try:
		in_temp = open( in_tempname, 'w+t' )
		in_temp.close()
	except:
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, value
			print >> stderr, "could not open in_temp file", in_tempname

	try:
		print 'in_temp:', in_temp
		print 'in_temp.name:', in_temp.name
		in_temp.write( text )
		in_temp.seek( 0 )	# rewind; needed?
	except:
		print >> stderr, "could not write in_temp file"

	try:
		out_temp = open( out_tempname, 'w+t' )
		print 'out_temp:', out_temp
		print 'out_temp.name:', out_temp.name
		out_temp.close()
	except:
		type, value, tb = exc_info()
		if settings.DEBUG == True:
			print >> stderr, "could not open out_temp file", out_tempname

	mosespath = os.path.join( settings.MOSES_HOME, "bin/moses" )
	mosesini  = os.path.join( settings.MOSES_DECODER, "sample-models", "phrase-model/moses.ini" )
#	cmdline = mosespath + ' -f phrase-model/moses.ini < phrase-model/in > out'
#	cmdline = mosespath + ' -f phrase-model/moses.ini < phrase-model/in'
	cmdline = mosespath + ' -f ' + mosesini + ' < ' + in_temp.name + ' > ' + out_temp.name

	if settings.DEBUG == True:
		print >> stderr, cmdline

	translation = "i do not know"

	saveddir = os.getcwd()
	os.chdir( settings.MOSES_DECODER )

	p = subprocess.Popen( cmdline, shell = True, stdout = subprocess.PIPE )
	resp = p.stdout.read()
	print >> stderr, "resp: |%s|" % resp

	os.chdir( saveddir )

	in_temp.close()		# Automatically cleans up the file if tempfile
	print 'in_temp exists after close:', os.path.exists( in_temp.name)

	out_temp = open( out_tempname, 'r+t' )
	translation = out_temp.read()
	out_temp.close()	# Automatically cleans up the file if tempfile
	print 'out_temp exists after close:', os.path.exists( out_temp.name)

	"""
	cmdline = "perl " + perlpath + " --query \'" + query_str + "\'"

#	cmdline = 'perl -d ' + perlpath + ' --query "' + query_str + '"'

	print cmdline, "\n"
	p = subprocess.Popen( cmdline, shell = True, stdout = subprocess.PIPE )
	resp_str = p.stdout.read()
	print >> stderr, "resp_str: |%s|" % resp_str

#	msg = "%s" % str( p.returncode )			# returncode is None, also with Catmandu error
#	print >> stderr, "returncode: %s" % msg

	# simplistic check, until we can grab the perl error
	if len( query_str ) > 0 and resp_str == "":
		raise Exception( "CQL to ElasticSearch conversion error" )
	"""
	return translation



@csrf_exempt
def moses( request ):
	if settings.DEBUG == True:
		print >> stderr, "moses()"
	#	print >> stderr, req_dict

	req_dict = request.REQUEST
	try:
		text = req_dict[ 'text' ]
	except( KeyError ):
		msg = "key error on 'text'"
		if settings.DEBUG == True:
			print >> stderr, msg

		try:
			remote_addr = request.META[ 'REMOTE_ADDR' ]
		except:
			remote_addr = ""
		extra = { 'REMOTE_ADDR' : remote_addr }
		logger.warn( msg, extra = extra )

		resp_dict = { 'status' : 'error', 'msg' : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	if settings.MOSES_DECODER == "":
		resp_dict =  { "status" : "error", "translation" : "", "msg" : "moses translator not available" }
	else:
		try:
		#	translation = "I am a Hamburger"
			translation = execute( text )
			resp_dict =  { "status" : "ok", "translation" : translation }
		except:
			type, value, tb = exc_info()
			if settings.DEBUG == True:
				print >> stderr, value
			resp_dict =  { "status" : "error", "translation" : "", "msg" : "translation failed" }

	json_list = json.dumps( resp_dict )
	ctype = 'application/json; charset=UTF-8'
	return HttpResponse( json_list, content_type = ctype )

# [eof]
