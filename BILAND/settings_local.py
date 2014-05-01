# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Copyright:	Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BILAND
Name:		settings_local.py
Version:	0.34
Goal:		local settings for BILAND project on fietstas2

Django admin:	Username: 		aclaan
				E-mail address:	a.c.laan@uva.nl
				Password:		djangobiland

FL-17-Oct-2011: Created
FL-17-Sep-2013: fietstas2 is the new production server for Texcavator
FL-20-Dec-2013: Changed
"""

import os
import sys
from socket import gethostname, gethostbyaddr


PROJECT_ROOT   = os.path.abspath( os.path.dirname( __file__ ) )
PROJECT_PARENT = os.path.dirname( PROJECT_ROOT )
PROJECT_GRANNY = os.path.dirname( PROJECT_PARENT )
PROJECT_CELERY = False				# do we need Celery?
# now also disabled automatic starting of celeryd in /etc/rc.d/rc.local
PROJECT_HAYSTACK = ''

sys.path.append( PROJECT_PARENT )


from BILAND.__init__ import DEBUG

if DEBUG == True:
	print >> sys.stderr, "PROJECT_GRANNY:", PROJECT_GRANNY
	print >> sys.stderr, "PROJECT_PARENT:", PROJECT_PARENT
	print >> sys.stderr, "PROJECT_ROOT:",   PROJECT_ROOT
	print >> sys.stderr, "Python version:", sys.version
	print >> sys.stderr, "PYTHONPATH:",     sys.path

PATH = os.environ[ "PATH" ]
try:
	PATH.index( "perlbrew" )
except:		# add perlbrew to PATH; take PERLBREW_PATH from .perlbrew/init
	PERLBREW_PATH="/datastore/alaan2/perl5/perlbrew/bin:/datastore/alaan2/perl5/perlbrew/perls/perl-5.18.1/bin"
	os.environ[ "PATH" ] = PERLBREW_PATH + ':' + os.environ[ "PATH" ]
if DEBUG == True:
	print >> sys.stderr, "PATH:", os.environ[ "PATH" ]

from django import get_version
django_version_str = get_version()
django_version_lst =  django_version_str.split( '.' )
DJANGO_MAJ_MIN = float( django_version_lst[0] + '.' + django_version_lst[1] )	# ignore [2] = rev
if DEBUG == True:
	print >> sys.stderr, "Django version: %s" % DJANGO_MAJ_MIN

# Which hardware?
( hostname, aliaslist, ipaddrlist ) = gethostbyaddr( gethostname() )
HOSTNAME = hostname
if DEBUG == True:
	print >> sys.stderr, "running on: %s" % HOSTNAME

# my network starts slow, and when the celeryd daemon starts the hostname is not yet known
#if hostname != "u017343.science.uva.nl":		# Fons local PC O&O network
#if hostname != "u017343.1x.uva.nl":				# Fons local PC
#	raise Exception( "Your host '%s' was not found!" % hostname )
#	sys.exit( 1 )

#DEV_SERVER_PORT = 8000		# $ python manage.py runserver 0.0.0.0:8000
DEV_SERVER_PORT = 8001		# $ python manage.py runserver 0.0.0.0:8001
WEB_SERVER_PORT = 8008
SUB_SITE = "/biland/"		# used for WEB_SERVER_PORT
if DEBUG == True:
	print >> sys.stderr, "DEV_SERVER_PORT: %s" % DEV_SERVER_PORT
	print >> sys.stderr, "WEB_SERVER_PORT: %s" % WEB_SERVER_PORT
	print >> sys.stderr, "SUB_SITE: %s" % SUB_SITE


ELASTICSEARCH_HOST = "localhost"	# 
ELASTICSEARCH_PORT = 9200
#ELASTICSEARCH_HOST = "zookst22.science.uva.nl"	# 
#ELASTICSEARCH_PORT = 9004						# zookst22
#ELASTICSEARCH_HOST = "zookst23.science.uva.nl"	# 
#ELASTICSEARCH_PORT = 8005						# zookst23
#ES_INDEX_KONBIB    = "kb_2013"
ES_INDEX_KONBIB    = "kb_sample"
ES_INDEX_STABI     = "stabi"
#ES_INDEX_DOCTYPE_KONBIB = "doc"			# kb_all
ES_INDEX_DOCTYPE_KONBIB = "doc"			# kb_sample
#ES_INDEX_DOCTYPE_KONBIB = "expression"	# kb_2013
ES_INDEX_DOCTYPE_STABI  = "doc"

# Notice: for retrieving (not storing!) documents, 
# sometimes DSTORE_KBRESOLVER is used inside the code
#XTAS_DATASTORE = "DSTORE_MONGODB"				# NOT ON zookst18 !
XTAS_DATASTORE  = "DSTORE_ELASTICSEARCH"
XTAS_COLLECTION = ES_INDEX_KONBIB
# default collection; notice: hardcoded in:
#	BiLand/services/static/xslt/sru.kb.xsl 
#	BiLand/BILAND/templates/index.html (radio buttons)

XTAS_FLUSH_CACHE = False						# default False for ES, True is for testing

if XTAS_DATASTORE == "DSTORE_ELASTICSEARCH":
#	XTAS_HOST        = 'zookst18.science.uva.nl'	# with ElasticSearch Ork
#	XTAS_HOST        = '192.168.70.31'				# zookst22 infiniband
#	XTAS_HOST        = 'zookst22.science.uva.nl'	# 
	XTAS_HOST        = 'localhost'	# 
	XTAS_PREFIX      = 'api'
#	XTAS_PORT        =  9006						# zookst22 
	XTAS_PORT        =  8088						# localhost Janneke 
	XTAS_API_KEY     = 'xtasapikey'						# no other keys
	XTAS_DOC_ID      = "METADATAKEY"				# new: used by Ridho
	XTAS_DOCS_SELECT = "LIST"						# only by docid list

else:
	print >> sys.stderr, "No xTAS datastore ?"
	sys.exit( 1 )

#	XTAS_HOST    = 'zookst17.science.uva.nl'	# spare server
#	XTAS_PREFIX  = 'legacy'

XTAS_MAX_CLOUD_DOCS_WARN  =  2500				# servers
XTAS_MAX_CLOUD_DOCS_ERROR = 10000				# servers


STABI_IMG_DOWNLOAD = "BILAND_scans/_Preussische_Amtspresse_35pct"

QUERY_DATA_DOWNLOAD_ALLOW  = True
QUERY_DATA_DOWNLOAD_DETACH = True		# when True QUERY_DATA_VPYTHON_PATH is needed
QUERY_DATA_DOWNLOAD_PATH   = os.path.join( PROJECT_GRANNY, "BILAND_download/query_data" )
QUERY_DATA_VPYTHON_PATH    = os.path.join( PROJECT_GRANNY, "python266" )	# virtual python
QUERY_DATA_CHUNK_SIZE      = 100		# no. of documents from ES with 1 query
QUERY_DATA_DELETE_DATA     = True		# delete query download data
QUERY_DATA_EXPIRE_DAYS     = 1			# delete after one day

# translation
GOOGLE_TRANSLATE = True
MOSES_TRANSLATE  = False
MOSES_HOME       = ""				# "/datastore/aclaan/moses-smt/moses"
MOSES_DECODER    = ""				# os.path.join( PROJECT_GRANNY, "mosesdecoder" )

# user action logging
ILPS_LOGGING = False				# if True, also uncomment code in base.html

if DEBUG == True:
	print >> sys.stderr, "XTAS_HOST:           %s" % XTAS_HOST
	print >> sys.stderr, "XTAS_PORT:           %s" % XTAS_PORT
	print >> sys.stderr, "XTAS_PREFIX:         %s" % XTAS_PREFIX
	print >> sys.stderr, "XTAS_API_KEY:        %s" % XTAS_API_KEY

	print >> sys.stderr, "XTAS_MAX_CLOUD_DOCS_WARN:  %s" % XTAS_MAX_CLOUD_DOCS_WARN
	print >> sys.stderr, "XTAS_MAX_CLOUD_DOCS_ERROR: %s" % XTAS_MAX_CLOUD_DOCS_ERROR

	print >> sys.stderr, "ELASTICSEARCH_HOST:  %s" % ELASTICSEARCH_HOST
	print >> sys.stderr, "ELASTICSEARCH_PORT:  %s" % ELASTICSEARCH_PORT
	print >> sys.stderr, "ES_INDEX_KONBIB:     %s" % ES_INDEX_KONBIB
	print >> sys.stderr, "ES_INDEX_STABI:      %s" % ES_INDEX_STABI
	print >> sys.stderr, "STABI_IMG_DOWNLOAD:  %s" % STABI_IMG_DOWNLOAD

	print >> sys.stderr, "QUERY_DATA_DOWNLOAD_ALLOW:  %s" % QUERY_DATA_DOWNLOAD_ALLOW
	print >> sys.stderr, "QUERY_DATA_DOWNLOAD_DETACH: %s" % QUERY_DATA_DOWNLOAD_DETACH
	print >> sys.stderr, "QUERY_DATA_DOWNLOAD_PATH:   %s" % QUERY_DATA_DOWNLOAD_PATH
	print >> sys.stderr, "QUERY_DATA_VPYTHON_PATH:    %s" % QUERY_DATA_VPYTHON_PATH
	print >> sys.stderr, "QUERY_DATA_CHUNK_SIZE:      %s" % QUERY_DATA_CHUNK_SIZE
	print >> sys.stderr, "QUERY_DATA_DELETE_DATA:     %s" % QUERY_DATA_DELETE_DATA
	print >> sys.stderr, "QUERY_DATA_EXPIRE_DAYS:     %s" % QUERY_DATA_EXPIRE_DAYS

	print >> sys.stderr, "GOOGLE_TRANSLATE: %s" % GOOGLE_TRANSLATE
	print >> sys.stderr, "MOSES_TRANSLATE:  %s" % MOSES_TRANSLATE
	print >> sys.stderr, "MOSES_HOME:       %s" % MOSES_HOME
	print >> sys.stderr, "MOSES_DECODER:    %s" % MOSES_DECODER

	print >> sys.stderr, "ILPS_LOGGING:     %s" % ILPS_LOGGING

# database settings for sqlite3
#DATABASE_ENGINE   = 'django.db.backends.sqlite3'
#DATABASE_NAME     = os.path.join( PROJECT_ROOT, 'BILANDpython256.db' )		# sqlite3 path
#DATABASE_USER     = ''
#DATABASE_PASSWORD = ''

# database settings for mysql
DATABASE_NAME     = 'test_db_texcavator'
DATABASE_USER     = 'root'
#DATABASE_ENGINE   = 'django.db.backends.sqlite3'
DATABASE_ENGINE   = 'django.db.backends.mysql'
DATABASE_PASSWORD = 'geheim'
#DATABASE_ENGINE   = 'django.db.backends.postgresql_psycopg2'
#DATABASE_PASSWORD = 'postgresbiland'

DATABASES = {
	'default': {
		'ENGINE'   : DATABASE_ENGINE,		# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
		'NAME'     : DATABASE_NAME,			# Or path to database file if using sqlite3.
		'USER'     : DATABASE_USER,			# Not used with sqlite3.
		'PASSWORD' : DATABASE_PASSWORD,		# Not used with sqlite3.
		'HOST'     : '',					# Set to empty string for localhost. Not used with sqlite3.
		'PORT'     : '',					# Set to empty string for default. Not used with sqlite3.
	#	'OPTIONS'  : {
	#		'unix_socket' : '/tmp/mysql.sock'	# instead of default /var/lib/mysql/mysql.sock
	#	},
	}
}

if PROJECT_CELERY:
	CELERY_OWNER = "aclaan"			# who started celeryd ?
	CELERYD_LOG_FILE = os.path.join( PROJECT_ROOT, "BILAND_Celery.log" )
	if DEBUG == True:
		print >> sys.stderr, "CELERYD_LOG_FILE: %s" % CELERYD_LOG_FILE
else:
	CELERY_OWNER = None

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
    },
}

# [eof]
