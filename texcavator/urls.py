# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.http import HttpResponse

from django.views.generic import RedirectView, TemplateView
urlpatterns = patterns( '',
	url( r'^favicon\.ico$', RedirectView.as_view( url = '/static/image/icon/favicon.ico' ) ),
	url( r'^robots\.txt$', TemplateView.as_view( template_name = 'robots.txt', content_type = 'text/plain' ) ),
)

urlpatterns += patterns( '', 
	# Uncomment the admin/doc line below to enable admin documentation:
	url( r'^admin/doc/', include( 'django.contrib.admindocs.urls' ) ),

	# Uncomment the next line to enable the admin:
	url( r'^admin/', include( admin.site.urls) ),

	url( r'^js/(?P<path>.*)$', 'django.views.static.serve', { 
		'document_root':'js/', 
		'show_indexes': True
	}),
	
	url( r'^$', 'texcavator.views.index', name="index" ),

	url( r'^login/ajax/$', 'texcavator.views.loginajax' ),
	url( r'^login$', 'texcavator.views.user_login' ),
	
	url( r'^services/', include( 'services.urls' ) ),
	url( r'^lexicon/', include( 'lexicon.urls' ) ),
	url( r'^list/', include( 'list.urls' ) ),
	url( r'^query/', include( 'query.urls' ) ),

	# Not used?
	url( r'^login/$', 'django.contrib.auth.views.login' ),
	url( r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 
		'django.contrib.auth.views.password_reset_confirm', 
		{'template_name' : 'registration/password_reset.html',  'post_reset_redirect': '/logout/' } ),
	)
