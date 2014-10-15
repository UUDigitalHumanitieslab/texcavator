# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Copyright:    Daan Odijk, Fons Laan, ILPS-ISLA, University of Amsterdam
Project:    BiLand
Name:        settings.py
Version:    0.33
Goal:        Django settings for BiLand project.
Python:        With multiple python versions, care should be taken not to mix their 
            libraries. Switching between versions with a script is convenient, 
            but not sufficient; with
                $ ./manage.py runserver 0.0.0.0:8001
            the shell might start an obsolete system python, while
                $ python manage.py runserver 0.0.0.0:8001
            should be ok.
            Start with $ Python -V to check the version. 

DO-%%-%%%-2011: Created for WAHSP
FL-17-Oct-2011: hostname settings in settings_local.py
FL-28-Mar-2013: Added django-socialregistration (OAuth for Clarin)
FL-13-Mar-2013: Django-1.5 requires ALLOWED_HOSTS
FL-04-Jul-2013: WAHSP -> BILAND app
FL-12-Nov-2013: Changed
"""

import os
import sys

from settings_local import PROJECT_GRANNY, PROJECT_PARENT, PROJECT_ROOT

PROJECT_GRANNY = os.path.normpath( PROJECT_GRANNY )        # zap trailing `/'
PROJECT_PARENT = os.path.normpath( PROJECT_PARENT )        # zap trailing `/'
PROJECT_ROOT   = os.path.normpath( PROJECT_ROOT )        # zap trailing `/'

from texcavator.__init__ import DEBUG
TEMPLATE_DEBUG = DEBUG

# ADMINS
# MANAGERS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'
#LANGUAGE_CODE = 'nl-nl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = ''
# To collect the static files in the STATIC_ROOT dir: 
#   $ ./manage.py collectstatic
# Notice: staticfiles with dev server requires DEBUG = True
STATIC_ROOT = os.path.join( PROJECT_GRANNY, "texcavator_static" ) + os.sep

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
# '/biland_static/' literal also in apache config & possibly in *.js files: so change together
STATIC_URL = '/static/'
if DEBUG == True:
    print >> sys.stderr, "STATIC_URL:", STATIC_URL

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
# add trailing `/'
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join( PROJECT_ROOT, "static" ) + os.sep,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*j9i^g9&78r-_9l%y$8ddt+kb4zgbx@!thm6sz64n05%hu(%8t'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.locale.LocaleMiddleware',                # i18n
)

ROOT_URLCONF = 'texcavator.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join( PROJECT_ROOT, "templates" ),
)

INSTALLED_APPS = (
    'django.contrib.auth',        # required for admin
    'django.contrib.admin',        # managers admin site
    'django.contrib.admindocs',    # managers admin docs
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',

    'services',            # biland
    'query',

    'djcelery'

)

# CELERY SETTINGS
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Local-memory caching
# If you want the speed advantages of in-memory caching but don't have the capability of running Memcached, 
# consider the local-memory cache backend. This cache is multi-process and thread-safe.
# Note that each process will have its own private cache instance, which means no cross-process caching is possible. 
# This obviously also means the local memory cache isn't particularly memory-efficient, so it's probably not a good 
# choice for production environments. It's nice for development.
# -> settings_local.py
"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}
"""

# Logging setup taken from http://ianalexandr.com/blog/getting-started-with-
# django-logging-in-5-minutes.html
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/jvdzwaan/Texcavator/texcavator/' \
                        'Texcavator_Django.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'texcavator': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'services': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'elasticsearch': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'elasticsearch.trace': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

# django-registration
ACCOUNT_ACTIVATION_DAYS = 2
LOGIN_REDIRECT_URL = '/'

# local settings: db, ...
try:
    from settings_local import *
except ImportError:
    print >> sys.stderr, "No settings_local"
    pass

# [eof]
