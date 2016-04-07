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
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve

from .views import index, user_login, user_logout

admin.autodiscover()

urlpatterns = [
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/image/icon/favicon.ico', permanent=False)),
    url(r'^robots\.txt$',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    # Enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # TODO: is this the proper way to refer to locally served JavaScripts?
    url(r'^js/(?P<path>.*)$', serve, {'document_root': 'js/', 'show_indexes': True}),

    url(r'^$', index, name='index'),
    url(r'^login$', user_login),
    url(r'^logout$', user_logout),

    url(r'^services/', include('services.urls')),
    url(r'^query/', include('query.urls')),

    url(r'^shico/', TemplateView.as_view(template_name='shico.html'), name='shico'),
]

if settings.DEBUG:
    urlpatterns.extend([
        url(r'^404/$', TemplateView.as_view(template_name='404.html')),
        url(r'^500/$', TemplateView.as_view(template_name='500.html')),
    ])
