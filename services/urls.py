# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project		BiLand
Name:		urls.py
Version:	0.2
Goal:		services/urls definitions

FL-26-Mar-2013: Created
FL-09-Sep-2013: Changed
"""

from django.conf.urls import patterns, include, url 

# some URLs do not end with '$' because their path varies and may be longer
urlpatterns = patterns( 'services.views',
	url( r'doc_count/$',       'doc_count' ),

	url( r'celery/$',          'proxy' ),
	url( r'export/$',          'proxy' ),

	url( r'cloud/$',          'cloud' ),

	url( r'kb/resolver/$', 'retrieve_kb_resolver'),
	url( r'logger/$',          'proxy' ),
	url( r'retrieve/',         'proxy' ),
	url( r'search/$',          'search' ),
	url( r'scan/$',            'proxy' ),
	url( r'cql2es/$',          'test_cql2es' ),
)

# [eof]
