# -*- coding: utf-8 -*-

# FL-26-Aug-2013:	Changed

from django.conf.urls import patterns, include, url

import djcelery.views

urlpatterns = patterns( '',
	url( r'^$', 'lexicon.views.index' ),

	url( r'^(?P<lexiconID>\d+)/aggregation?$', 'lexicon.views.aggregation' ),

	url( r'^(?P<id>\d+)/?$', 'lexicon.views.item' ),

	url( r'^timeline/(?P<lexiconID>\d+)?$', 'lexicon.views.bursts' ),
	url( r'^timeline/(?P<lexiconID>\d+)?/(?P<resolution>\w+)$', 'lexicon.views.bursts' ),

	url( r'^timestamp/$',						'lexicon.views.timestamp_refresh' ),
	url( r'^stopwords/save/$',					'lexicon.views.stopwords_save' ),
	url( r'^stopwords/delete/$',				'lexicon.views.stopwords_delete' ),
	url( r'^stopwords/retrieve/string/$',		'lexicon.views.stopwords_retrieve_string' ),
	url( r'^stopwords/retrieve/table/$',		'lexicon.views.stopwords_retrieve_table' ),

	url( r'^download/prepare/$',					'lexicon.download.download_prepare' ),
	url( r'^download/data/(?P<zip_basename>.*)$',	'lexicon.download.download_data' ),

	url( r'^tasks/(?P<task_id>[\w\d\-]+)/done/?$',      djcelery.views.is_task_successful, name="celery-is_task_successful" ),
	url( r'^tasks/(?P<task_id>[\w\d\-]+)/(status)?/?$', djcelery.views.task_status,        name="celery-task_status" ),
)

# [eof]
