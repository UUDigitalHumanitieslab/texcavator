# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Copyright:	Fons Laan, ILPS-ISLA, University of Amsterdam
Project		BiLand
Name:		urls.py
Version:	0.22
Goal:		main url definitions

DO-%%-%%%-2011: Created
FL-28-Mar-2012: Added django-socialregistration (OAuth for Clarin)
FL-04-Jul-2013: -> BILAND app
FL-26-Aug-2013: Changed
"""

from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.http import HttpResponse

if settings.DJANGO_MAJ_MIN < 1.5:
	from django.views.generic.simple import direct_to_template
	urlpatterns = patterns( 'django.views.generic.simple',
		url( r'^favicon\.ico$',	'redirect_to',        { 'url': '/static/image/icon/favicon.ico' } ),
		url( r'^robots\.txt$',	'direct_to_template', { 'template': 'robots.txt', 'mimetype': 'text/plain' } ),
		url( r'^js/tests/$',    'redirect_to',        { 'url': '/js/tests/index.html' } ),
	)
else:
	from django.views.generic import RedirectView, TemplateView
	urlpatterns = patterns( '',
		url( r'^favicon\.ico$', RedirectView.as_view( url = '/static/image/icon/favicon.ico' ) ),
		url( r'^js/tests/$',    RedirectView.as_view( url = '/js/tests/index.html' ) ),
		url( r'^robots\.txt$',  TemplateView.as_view( template_name = 'robots.txt', content_type = 'text/plain' ) ),
	)


urlpatterns += patterns( '', 
	# Examples:
	# url( r'^$', 'BILAND.views.home', name='home' ),
	# url( r'^BILAND/', include('BILAND.foo.urls') ),

	# Uncomment the admin/doc line below to enable admin documentation:
	url( r'^admin/doc/', include( 'django.contrib.admindocs.urls' ) ),

	# Uncomment the next line to enable the admin:
	url( r'^admin/', include( admin.site.urls) ),

	# OAuth for Clarin
#	url( r'^social/', include( 'socialregistration.urls', namespace = 'socialregistration' ) ),

	url( r'^js/(?P<path>.*)$', 'django.views.static.serve', { 
		'document_root':'js/', 
		'show_indexes': True
	}),

#	url( r'^services/', 'services.views.proxy' ),
	url( r'^services/',	include( 'services.urls' ) ),

	url( r'^lexicon/',	include( 'lexicon.urls' ) ),
	url( r'^list/',		include( 'list.urls' ) ),

#	url( r'^accounts/', include( 'registration.backends.default.urls' ) ),
	url( r'^login/$',		'django.contrib.auth.views.login' ),
	url( r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name' : 'registration/password_reset.html',  'post_reset_redirect': '/logout/' } ),
	url( r'^login/ajax/$',	'BILAND.views.loginajax' ),
	url( r'^texcavator/',	'BILAND.views.texcavator', name="texcavator" ),
	url( r'^index/',		'BILAND.views.index',      name="index" ),
	url( r'^$',				'BILAND.views.index',      name="index" ),
)

