# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project		BiLand
Name:		urls.py
Version:	0.21
Goal:		list/urls definitions

FL-15-Nov-2011: Created
FL-26-Aug-2013: Changed
"""

from django.conf.urls.defaults import *

urlpatterns = patterns( 'list.views',
	url( r'^http404$',                            'http404' ),
	url( r'^http500$',                            'http500' ),
	url( r'^testpost/$',                          'testpost' ),
	url( r'^(?P<lex_id1>\d+),(?P<lex_id2>\d+)/$', 'compare_lexicons' ),
	url( r'^(?P<lex_id>\d+)/docs/$',              'list_lexicon_docs' ),
	url( r'^(?P<lex_id>\d+)/words/$',             'list_lexicon_words' ),
	url( r'^(?P<lex_id>\d+)/$',                   'list_lexicon' ),
	url( r'^all/$',                               'list_lexicons' ),
	url( r'^$',                                   'list_lexicons' ),
)

# [eof]
