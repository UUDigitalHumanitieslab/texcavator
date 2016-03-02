# -*- coding: utf-8 -*-
"""URL mappings for the services app"""
from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^doc_count/$', doc_count),

    url(r'^cloud/$', tv_cloud),
    url(r'^export_cloud/$', export_cloud),

    url(r'^task_status/(?P<task_id>[\w-]+)$', check_status_by_task_id),
    url(r'^cancel_task/(?P<task_id>[\w-]+)$', cancel_by_task_id),

    url(r'^kb/resolver/$', retrieve_kb_resolver),
    url(r'^retrieve/(?P<doc_id>[-\w:]+)', retrieve_document),
    url(r'^search/$', search),

    url(r'^scan/$', download_scan_image),
    url(r'^logger/$', log),

    url(r'^metadata/$', metadata),

    url(r'^stem/$', stemmed_form)
]
