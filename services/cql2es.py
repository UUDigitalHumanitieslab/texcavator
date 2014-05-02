# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Copyright:	Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		cql2es.py
Version:	0.21
Goal:		Convert a CQL query to an ElasticSearch query
			cql.2es.pl does the basic conversion

def cql2es_error( msg )
def execute( query_str )
def callperl( query_str, literal )
def add_phrase( es_query )

FL-13-Feb-2013: Created
FL-26-Aug-2013: Changed
"""

import os
#import re
from sys import stderr, exc_info
from types import *

import base64
import subprocess
import json

from django.conf import settings
from django.http import HttpResponse

#from settings import PROJECT_ROOT
from BILAND.settings import PROJECT_PARENT, PROJECT_ROOT, DEBUG
#try:
#	from BILAND.settings import PROJECT_PARENT, PROJECT_ROOT, DEBUG
#except:
#	PROJECT_PARENT="/datastore/aclaan/python/django/biland/BiLand"
#	PROJECT_ROOT="/datastore/aclaan/python/django/biland/BiLand/BILAND"
#	DEBUG = False


def cql2es_error( exc_value, query_str ):
	if DEBUG: print >> stderr, exc_value
	err = "Query:</br>" + query_str + "</br></br>"
	err += "CQL to ElasticSearch conversion error,</br>please adapt your query."

	if DEBUG:
		print >> stderr, "cql2es_error():", err.encode( "utf-8" )

	resp_dict =  { "status" : "error", "msg" : err.encode( "utf-8" ) }
	json_list = json.dumps( resp_dict )
	ctype = 'application/json; charset=UTF-8'

	return HttpResponse( json_list, content_type = ctype )



def execute( query_str ):
#	print >> stderr, "execute()"

	# select the perl we want
#	os.environ[ "PATH" ] = "/home/aclaan/perl5/perlbrew/bin:/home/aclaan/perl5/perlbrew/perls/perl-5.10.1/bin"

#	cmdline = "perl -v"
#	cmdline = 'perl /home/aclaan/perl5/cql2es.pl --query "' + query_str + '"'
#	perlpath = os.path.join( PROJECT_ROOT, "services", "cql2es.pl" )
	perlpath = os.path.join( PROJECT_PARENT, "services", "cql2es.pl" )	# new Django-1.5 dir structure
	cmdline = 'perl ' + perlpath + ' --query "' + query_str + '"'
#	cmdline = 'perl ' + perlpath + ' --query \"' + query_str + '\"'

#	query_str = re.sub(r'\\', r'\\\\', query_str)
#	query_str = re.sub(r'"', '\\"', query_str)


#	cmdline = "perl " + perlpath + " --query \'" + query_str + "\'"			# OK, but not with Kellogg's
#	cmdline = 'perl -d ' + perlpath + ' --query "' + query_str + '"'

	try:
	#	query_base64 = base64.b64encode( query_str )
		query_base64 = base64.b64encode( query_str.encode( "utf-8" ) )
	except:
		type, value, tb = exc_info()
		print >> stderr, "b64encode failed:", value

	if DEBUG:
		print >> stderr, query_base64.encode( "utf-8" )

	cmdline = "perl " + perlpath + " --query \'" + query_base64 + "\'"


	print >> stderr, cmdline, "\n"
	p = subprocess.Popen( cmdline, shell = True, stdout = subprocess.PIPE )
#	p = subprocess.Popen( cmdline, shell = False, stdout = subprocess.PIPE )
	resp_str = p.stdout.read()

	if DEBUG:
		# the print fails with apache with accented chars, but not with dev server ??
		# 'ascii' codec can't encode character ...: ordinal not in range(128)",
	#	print >> stderr, "\nresp_str: |%s|" % resp_str.decode( "utf-8" )
		pass

#	msg = "%s" % str( p.returncode )			# returncode is None, also with Catmandu error
#	print >> stderr, "returncode: %s" % msg

	# simplistic check, until we can grab the perl error
	if len( query_str ) > 0 and resp_str == "":
		raise Exception( "CQL to ElasticSearch conversion error" )

	return resp_str



def callperl( query_str, literal ):
#	print >> stderr, "callperl()"

	resp_str = execute( query_str )
	len_resp_str = len( resp_str )
#	print >> stderr, "response:", resp_str

	if len_resp_str == 0:
		es_query = {}
	else:
		try:
			es_query = eval( resp_str )		# string -> dict
		except: 							# unexpected EOF while parsing
			type, value, tb = exc_info()
			print >> stderr, "error: %s" % value
			es_query = {}

#	print type( es_query )
#	print es_query

	if literal == True:
		# add { "type" : "phrase" } to query for literal search
		es_query = add_phrase( es_query)
		if DEBUG:
			# the returned es_query is a dict
			print >> stderr, "es_phrase:", str( es_query ).encode( "utf-8" )

	# add outer level "query" key if non-empty
	es_query2 = {}
	if es_query != {}:
		es_query2[ "query" ] = es_query
	#	print es_query2[ "query" ]
	#	print es_query2

	return json.dumps( es_query2 )



def add_phrase( es_query ):
	print >> stderr, "add_phrase()"
	# {"bool":{"must":[{"text_phrase":{"_all":{"query":"watervliegtuig in"}}},{"range":{"paper_dc_date":{"lte":"19451231"}}}]}}
	# this function assumes very specific ES query structure!
	try:
		in_list = es_query[ "bool" ][ "must" ]
	except:
		# different query than we expect
		# es_query is a dict
		print >> stderr, "es_query:", str( es_query ).encode( "utf-8" )
		return es_query

	out_list = []
	for in_dict in in_list: 
		for key in in_dict:
			print >> stderr, key, in_dict[ key ]
			if key == "text_phrase":
				in_query = in_dict[ "text_phrase" ][ "_all" ]
				out_query = {}
				out_query[ "query" ] = in_query[ "query" ]
				out_query[ "type" ]  = "phrase"

				all_dict = {}
				all_dict[ "_all" ] = out_query

				text_phrase_dict = {}
				text_phrase_dict[ "text_phrase" ] = all_dict
				out_list.append( text_phrase_dict )
			else:
				out_list.append( in_dict )

	must = {}
	must[ "must" ] = out_list
	es_phrase = {}
	es_phrase[ "bool" ] = must

	return es_phrase



if __name__ == '__main__':
#	query_str = "" 		# -> {} as query			# 84.192.350 hits; according to Daan there should now be 100.000.000
#	query_str = 'opium AND dc.date <= 19451231'				# 
#	query_str = 'opium AND paper_dc_date <= 19451231'		# 
#	query_str = "opium AND paper_dc_date <= 1945-12-31"		# 65321
#	query_str = "opium AND (paper_dc_date >= 1945-11-30 AND paper_dc_date <= 1945-12-31)";	# 4 hits
#												num_args
#	query_str = "watervliegtuig"				# 2	--query "watervliegtuig"			-> {"query": "watervliegtuig"}
#	query_str = "watervliegtuig in"				# 2	--query "watervliegtuig in"			-> error
#	query_str = '\"watervliegtuig in\"'			# 3	--query ""watervliegtuig in""		-> {}
#	query_str = '\\"watervliegtuig in\\"'		# 2	--query "\"watervliegtuig in\""		-> {"query": "watervliegtuig in"}
#	query_str = '\\\"watervliegtuig in\\\"'		# 2	--query "\"watervliegtuig in\"" 	-> {"query": "watervliegtuig in"}
#	query_str = '\\\\"watervliegtuig in\\\\"'	# 3	--query "\\"watervliegtuig in\\""	-> {}

#	query_str = '"watervliegtuig" AND paper_dc_date <= 19451231'			# OK
#	query_str = '"watervliegtuig in" AND paper_dc_date <= 19451231'			# OK
#	query_str = '\\"watervliegtuig in\\" AND paper_dc_date <= 19451231'		# cql error: unterminated string
#	query_str = '\\"watervliegtuig in\\" AND paper_dc_date <= 19451231'
	query_str = 'Kellogg AND paper_dc_date <= 19451231'						# OK
#	query_str = "Kellogg AND paper_dc_date <= 19451231"						# OK
#	query_str = "Kellogg's AND paper_dc_date <= 19451231"					# shell error
#	query_str = "Kellogg\'s AND paper_dc_date <= 19451231"					# shell error
#	query_str = "Kellogg\\'s AND paper_dc_date <= 19451231"					# shell error
#	q1 = "Kellogg's"
#	query_str = q1 + ' AND paper_dc_date <= 19451231'


	resp_str = execute( query_str )
	len_resp_str = len( resp_str )
#	print >> stderr, "resp_str: |%s|" % resp_str
#	print resp_str
#	print "length:", len_resp_str

	if len_resp_str == 0:
		es_query = {}
	else:
		try:
			print >> stderr, "resp_str: |%s|" % resp_str
			es_query = eval( resp_str )		# string -> dict
		except: 							# unexpected EOF while parsing
			type, value, tb = exc_info()
		#	print >> stderr, "resp_str: |%s|" % resp_str
		#	print >> stderr, "error: %s" % value.message	# BaseException.message has been deprecated as of Python 2.6
			print >> stderr, "error: %s" % value
			es_query = {}

	# add { "type" : "phrase" } to query for literal search
	es_query = add_phrase( es_query)
	print >> stderr, "es_phrase:", es_query

	# add outer level "query" key if non-empty
	es_query2 = {}
	if es_query != {}:
		es_query2[ "query" ] = es_query
	#	print es_query2[ "query" ]
	#	print es_query2

	print json.dumps( es_query2 )

# [eof]
