# -*- coding: utf-8 -*-
"""Local settings for Texcavator
"""

import os
import sys

# This determines the <title> of the web interface.
PROJECT_NAME = 'Texcavator'

# Project folders
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)
PROJECT_GRANNY = os.path.dirname(PROJECT_PARENT)

sys.path.append(PROJECT_PARENT)

# Deployment settings
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/
SECRET_KEY = '5at!yd@mwyn_^xn54m&rg%(6zqprm22^)lke5$v&)-s$+yfj1f'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = []
STATIC_ROOT = os.path.join(PROJECT_GRANNY, "texcavator_static") + os.sep
LOGGING_LOCATION = PROJECT_PARENT

# Elasticsearch settings
ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_USERNAME = None
ELASTICSEARCH_PASSWORD = None
ELASTICSEARCH_USE_SSL = False
ES_INDEX = 'kb'
ES_DOCTYPE = 'doc'

# Query settings
QUERY_ALLOW_LEADING_WILDCARD = False
QUERY_DATA_DOWNLOAD_ALLOW = True

QUERY_DATA_DOWNLOAD_PATH = os.path.join(PROJECT_GRANNY,
                                        "BILAND_download/query_data")

QUERY_DATA_MAX_RESULTS = 100000     # max no. of documents to be exported
QUERY_DATA_UNPRIV_RESULTS = 10000   # no. of documents to be exported for lesser privileged users
QUERY_DATA_CHUNK_SIZE = 1000		# no. of documents from ES with 1 query
QUERY_DATA_DELETE_DATA = True		# delete query download data
QUERY_DATA_EXPIRE_DAYS = 1			# delete after one day

# user action logging
ILPS_LOGGING = False				# if True, also uncomment code in base.html

# Database settings
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

# Global date range
TEXCAVATOR_DATE_RANGE = "18500101,19901231"

# Email settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

# Login URL
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Minimum and maximum number of words allowed in the word cloud
WORDCLOUD_MIN_WORDS = 1
WORDCLOUD_MAX_WORDS = 200

# Temporary setting for whether or not stemming is available
STEMMING_AVAILABLE = True

# Temporary setting for whether or not the hotfix for duplicate newspapers should be used
KB_HOTFIX_DUPLICATE_NEWSPAPERS = True
