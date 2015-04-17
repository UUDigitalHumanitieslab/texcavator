# -*- coding: utf-8 -*-
"""Texcavator settings
"""

import os
import sys

from settings_local import PROJECT_GRANNY, PROJECT_PARENT, PROJECT_ROOT
from texcavator.__init__ import DEBUG

PROJECT_GRANNY = os.path.normpath(PROJECT_GRANNY)      # zap trailing `/'
PROJECT_PARENT = os.path.normpath(PROJECT_PARENT)      # zap trailing `/'
PROJECT_ROOT = os.path.normpath(PROJECT_ROOT)          # zap trailing `/'

TEMPLATE_DEBUG = DEBUG

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
# LANGUAGE_CODE = 'nl-nl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# To collect the static files in the STATIC_ROOT dir:
#   $ ./manage.py collectstatic
# Notice: staticfiles with dev server requires DEBUG = True
STATIC_ROOT = os.path.join(PROJECT_GRANNY, "texcavator_static") + os.sep

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'
if DEBUG:
    print >> sys.stderr, "STATIC_URL:", STATIC_URL

# Additional locations of static files
# add trailing `/'
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, "static") + os.sep,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*j9i^g9&78r-_9l%y$8ddt+kb4zgbx@!thm6sz64n05%hu(%8t'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, "templates"),
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

    'services',
    'query',

    'djcelery',
    'django_nose'
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# CELERY SETTINGS
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Logging setup taken from http://ianalexandr.com/blog/getting-started-with-
# django-logging-in-5-minutes.html
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s " +
                      "[%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/jvdzwaan/Texcavator/texcavator/'
                        'Texcavator_Django.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'texcavator': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'services': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'query': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'elasticsearch': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'elasticsearch.trace': {
            'handlers': ['file'],
            'level': 'WARN',
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
