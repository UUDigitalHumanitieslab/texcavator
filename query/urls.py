# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url 

urlpatterns = patterns( 'query.views',
    url( r'^$', 'index' ),
    url( r'^(?P<query_id>\d+)/?$', 'query' ),
    url( r'^timeline/(?P<query_id>\d+)?/(?P<resolution>\w+)$', 'timeline' ),
    url(r'^create$', 'create_query'),
    url( r'^(?P<query_id>\d+)/delete$', 'delete' ),
    url( r'^(?P<query_id>\d+)/update$', 'update' ),
    url( r'^stopword/add$', 'add_stopword' ),
    url( r'^stopword/(?P<stopword_id>\d+)/delete$', 'delete_stopword' ),
    url( r'^stopwords$', 'stopwords' ),

    url( r'^download/prepare/$',                    'download_prepare' ),
)
