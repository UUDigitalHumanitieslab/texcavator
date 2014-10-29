# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		services/management/commands/addusers.py
Version:	0.1
Goal:		Add user accounts to the user table
			execute in the $BILAND_HOME directory:
				$ ./manage.py addusers

Notice:		Need YAML: $ pip install --verbose PyYAML
			Reads yaml file "users.yaml" from current directory

FL-30-Aug-2013: Created
FL-03-Sep-2013: Changed
"""

import os
from time import time
from sys import exc_info

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

import yaml


FILENAME = "users.yaml"


class Command( BaseCommand ):
	def handle( self, *args, **kwargs ):
		t1 = time()
		self.stdout.write( "\naddusers\n" )

		yaml_path = os.path.join( settings.PROJECT_PARENT, "services/management/commands", FILENAME )
		yaml_stream = file( yaml_path )

		users = yaml.load( yaml_stream )

		for usr in users:
			username = usr[ "username" ]
			password = usr[ "password" ]

			try:
				user = auth.authenticate( username = username, password = password )
				if not user:
					self.adduser( usr )
				else:
					self.stdout.write( "user %s already exists\n" % username )
			except:
				type, value, tb = exc_info()
				msg = "Authentication failed: %s\n" % value
				self.stdout.write(  msg )

		t2 = time()			# seconds since the epoch
		sec = (t2-t1)
		str_elapsed = str( round( sec, 2) ) + " sec"

		self.stdout.write( "finished in %s\n" % str_elapsed )


	def showuser( self, usr ):
		username = usr[ "username" ]
		password = usr[ "password" ]

		try:
			email = usr[ "email" ]
		except:
			email = ''

		try:
			first_name = usr[ "first_name" ]
		except:
			first_name = ''

		try:
			last_name = usr[ "last_name" ]
		except:
			last_name = ''

		self.stdout.write( "username: %s, password: %s, email: %s, first_name: %s, last_name: %s" % ( username, password, email, first_name, last_name ) )


	def adduser( self, usr ):
		username = usr[ "username" ]
		password = usr[ "password" ]

		try:
			email = usr[ "email" ]
		except:
			email = ''

		self.stdout.write( "adding user: %s\n" % username )
		user = User.objects.create_user( username, email, password )

		try:
			user.first_name = usr[ "first_name" ]
		except:
			user.first_name = ''

		try:
			user.last_name = usr[ "last_name" ]
		except:
			user.last_name = ''

		self.showuser( usr )

		user.save()

# [eof]

