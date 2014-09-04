# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url 

urlpatterns = patterns( 'query.views',
	url( r'^$', 'index' ),
	url( r'^(?P<query_id>\d+)/?$', 'query' ),
	url( r'^timeline/(?P<query_id>\d+)?/(?P<resolution>\w+)$', 'timeline' ),
    url(r'^create$', 'create_query'),
	url( r'^(?P<query_id>\d+)/delete$', 'delete' ),
)
