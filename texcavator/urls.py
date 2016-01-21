# -*- coding: utf-8 -*-
"""texcavator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/image/icon/favicon.ico')),
    url(r'^robots\.txt$',
        TemplateView.as_view(template_name='robots.txt',
                             content_type='text/plain')),

    # Enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'js/', 'show_indexes': True}),
    url(r'^$', 'texcavator.views.index', name='index'),

    url(r'^login$', 'texcavator.views.user_login'),
    url(r'^logout$', 'texcavator.views.user_logout'),

    url(r'^services/', include('services.urls')),
    url(r'^query/', include('query.urls')),

    # TODO: Not used? So, remove?
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm', {
            'template_name': 'registration/password_reset.html',
            'post_reset_redirect': '/logout/'
        }),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^500/$', TemplateView.as_view(template_name='500.html')),
        (r'^404/$', TemplateView.as_view(template_name='404.html')),
    )
