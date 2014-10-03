# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'services.views',

    url(r'doc_count/$', 'doc_count'),

    url(r'export_cloud/$', 'export_cloud'),

    url(r'cloud/$', 'tv_cloud'),
    url(r'task_status/(?P<task_id>[\w-]+)$', 'check_status_by_task_id'),

    url(r'kb/resolver/$', 'retrieve_kb_resolver'),
    url(r'retrieve/(?P<doc_id>[\w:]+)', 'retrieve_document'),
    url(r'search/$', 'search'),

    url(r'scan/$', 'proxy'),
    url(r'logger/$', 'proxy'),
)
