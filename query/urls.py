# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url 

urlpatterns = patterns( 'query.views',
	url( r'^(?P<query_id>\d+)/?$', 'query' ),
)
