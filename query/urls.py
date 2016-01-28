# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', index),

    url(r'^(?P<query_id>\d+)/?$', get_query),
    url('^create$', create_query),
    url(r'^(?P<query_id>\d+)/delete$', delete),
    url(r'^(?P<query_id>\d+)/update$', update),
    url(r'^(?P<query_id>\d+)/update_nr_results?$', update_nr_results),

    url(r'^stopword/add$', add_stopword),
    url(r'^stopword/(?P<stopword_id>\d+)/delete$', delete_stopword),
    url(r'^stopword/export$', export_stopwords),
    url(r'^stopwords$', stopwords),

    url(r'^timeline/(?P<query_id>\d+)?/(?P<resolution>\w+)$', timeline),

    url(r'^pillars$', retrieve_pillars),
    url(r'^timeframes$', retrieve_timeframes),

    url(r'^newspaper/export$', export_newspapers),

    url(r'^download/prepare/$', download_prepare),
    url(r'^download/(?P<zip_name>.*)$', download_data),
]
