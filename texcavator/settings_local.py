# -*- coding: utf-8 -*-
"""Local settings for Texcavator
"""

import os
import sys

from texcavator.__init__ import DEBUG

# This determines the <title> of the web interface.
PROJECT_NAME = 'Texcavator'

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)
PROJECT_GRANNY = os.path.dirname(PROJECT_PARENT)

sys.path.append(PROJECT_PARENT)

if DEBUG:
    print >> sys.stderr, "PROJECT_GRANNY:", PROJECT_GRANNY
    print >> sys.stderr, "PROJECT_PARENT:", PROJECT_PARENT
    print >> sys.stderr, "PROJECT_ROOT:",   PROJECT_ROOT
    print >> sys.stderr, "Python version:", sys.version
    print >> sys.stderr, "PYTHONPATH:",     sys.path

ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_USERNAME = None
ELASTICSEARCH_PASSWORD = None
ELASTICSEARCH_USE_SSL = False
ES_INDEX = 'kb'
ES_DOCTYPE = 'doc'

QUERY_DATA_DOWNLOAD_ALLOW = True

QUERY_DATA_DOWNLOAD_PATH = os.path.join(PROJECT_GRANNY,
                                        "BILAND_download/query_data")

QUERY_DATA_MAX_RESULTS = 100000     # max no. of documents to be exported
QUERY_DATA_CHUNK_SIZE = 1000		# no. of documents from ES with 1 query
QUERY_DATA_DELETE_DATA = True		# delete query download data
QUERY_DATA_EXPIRE_DAYS = 1			# delete after one day

# user action logging
ILPS_LOGGING = False				# if True, also uncomment code in base.html

if DEBUG:
    print >> sys.stderr, "ELASTICSEARCH_HOST:  %s" % ELASTICSEARCH_HOST
    print >> sys.stderr, "ELASTICSEARCH_PORT:  %s" % ELASTICSEARCH_PORT
    print >> sys.stderr, "ES_INDEX:     %s" % ES_INDEX

    print >> sys.stderr, "QUERY_DATA_DOWNLOAD_ALLOW:  %s" % \
        QUERY_DATA_DOWNLOAD_ALLOW
    print >> sys.stderr, "QUERY_DATA_DOWNLOAD_PATH:   %s" % \
        QUERY_DATA_DOWNLOAD_PATH
    print >> sys.stderr, "QUERY_DATA_CHUNK_SIZE:      %s" % \
        QUERY_DATA_CHUNK_SIZE
    print >> sys.stderr, "QUERY_DATA_DELETE_DATA:     %s" % \
        QUERY_DATA_DELETE_DATA
    print >> sys.stderr, "QUERY_DATA_EXPIRE_DAYS:     %s" % \
        QUERY_DATA_EXPIRE_DAYS

    print >> sys.stderr, "ILPS_LOGGING:     %s" % ILPS_LOGGING

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tex',
        'USER': 'tex',
        'PASSWORD': 'tex',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

TEXCAVATOR_DATE_RANGE = "18500101,19901231"

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

LOGIN_URL = '/'

# Temporary setting for whether or not stemming is available
STEMMING_AVAILABLE = True
