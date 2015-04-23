# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

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
