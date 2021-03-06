# -*- coding: utf-8 -*-
"""URL mappings for the services app"""
from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^doc_count/$', doc_count),

    url(r'^cloud/$', tv_cloud),
    url(r'^export_cloud/$', export_cloud, name='export_cloud'),

    url(r'^task_status/(?P<task_id>[\w-]+)$', check_status_by_task_id),
    url(r'^cancel_task/(?P<task_id>[\w-]+)$', cancel_by_task_id),

    url(r'^retrieve/(?P<doc_id>[-\w:]+)$', retrieve_document),
    url(r'^search/$', search),

    url(r'^kb/resolver/(?P<doc_id>[-\w:]+)$', retrieve_kb_resolver),

    url(r'^metadata/$', metadata),

    url(r'^heatmap/(?P<query_id>\d+)/(?P<year>[0-9]{4})$', heatmap),

    url(r'^stem/$', stemmed_form)
]
