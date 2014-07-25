# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Daan Odijk, Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/tasks.py
Version:	0.35
Goal:		lexicon/tasks
To do:		limit size of Celery log file

DO-%%-%%%-2011: Created
FL-25-Jan-2012: Only write from celery tasks to stdout/sdterr when DEBUG=True, 
				because we got complaints about the Huygens server. 
FL-22-Mar-2012: Changed recordPosition from relative to absolute counting
FL-03-Sep-2012: Celery-3: logger now defined at module level instead of function level
FL-14-Dec-2012: No more rate_limit
FL-25-Jan-2013: Strip ":ocr" from docID for ElasticSearch
FL-08-Feb-2013: date range as parameter; not from settings.py
FL-08-Mar-2013: docID switch for ElasticSearch
FL-10-Sep-2013: Changed

tasks:
	storeDigitaleDagbladenArticle( recordString, docID, lexiconID, startRecord, storeRecord = True )
		extract document metadata -> Django MySQL
"""

import os
from sys import stderr, exc_info
import json

from django.conf import settings
from django.http import HttpResponse

from celery.decorators import task
from celery import __version__ as celery__version__

#from BiLand.lexicon.download import get_es_chunk		# circular import problem?
#from BiLand.services.request import request2article_types, request2parms
#from BiLand.services.xtas import addtags_elasticsearch


#print >> stderr, "Celery version:", celery__version__
celery_version_lst = celery__version__.split( '.' )
celery_version_maj = int( celery_version_lst[ 0 ] )

if celery_version_maj >= 3:
	from celery.utils.log import get_task_logger	# celery-3: 
	logger = get_task_logger( __name__ ) 			# logger now defined at module level instead of function level

if settings.DEBUG == True:
	print >> stderr, "Celery maj version:", celery_version_maj

# Task should retry every now and then and update status of subtask:
# Problem: http://ask.github.com/celery/userguide/tasks.html#avoid-launching-synchronous-subtasks
# Solution: http://docs.celeryproject.org/en/latest/userguide/tasksets.html#task-set-callbacks

SRW_NS = "http://www.loc.gov/zing/srw/"
DDD_NS = "http://www.kb.nl/ddd" 
DC_NS  = "http://purl.org/dc/elements/1.1/"


def record_find_text( record, ns, field_name ):
	what = ".//{%s}%s" % ( ns, field_name )
	elem = record.find( what )

	if elem is None:
		text = ''
	else:
		text = elem.text.strip()

	msg = "name: %s, text: %s" % ( field_name, text )
	if settings.DEBUG == True:
		print >> stderr, msg

	return text

#@task( rate_limit = "50/s" )
@task
def storeDigitaleDagbladenArticle( recordString, docID, lexiconID, startRecord, storeRecord = True ):
	"""extract document metadata -> Django MySQL"""
	global logger
	if celery_version_maj < 3:
		logger = storeDigitaleDagbladenArticle.get_logger()
#	print >> stderr, "tasks.py/storeDigitaleDagbladenArticle()"

	msg = "Storing document %s for lexicon #%s" % ( docID, lexiconID )
	logger.info( msg )
	if settings.DEBUG == True:
		print >> stderr, msg

	from models import DigitaleDagbladenArticle, LexiconItem, LexiconArticle
	from datetime import datetime
	from django.db import DatabaseError, IntegrityError
	from lxml import etree

	record = etree.fromstring( recordString )		# parse xml string to etree object
	try:
		if storeRecord:
		#	title_long = record.find(".//{%s}title" % DC_NS).text[:255]
			title_long = record_find_text( record, DC_NS, "title" )
			title_short = title_long[:255]		# db field length

			# FL: change page db field from int to string
		#	page = int(record.find(".//{%s}page" % DDD_NS).text),
			page_str = record_find_text( record, DDD_NS, "page" )
			if page_str == '':
				page_num = 0
			else:
				try:
					page_num = int( page_str )
				except:
					page_num = 0

			# notice that 2 different namespaces are used
			article = DigitaleDagbladenArticle(
				identifier = docID,

				title = title_short,

			#	papertitle = record.find(".//{%s}papertitle" % DDD_NS).text,
				papertitle = record_find_text( record, DDD_NS, "papertitle" ),

			#	publisher = record.find(".//{%s}publisher" % DDD_NS).text,
				publisher = record_find_text( record, DDD_NS, "publisher" ),

				date = datetime.strptime( record.find( ".//{%s}date" % DC_NS ).text, '%Y/%m/%d %H:%M:%S' ),
			#	date_str = record_find_text( record, DC_NS, "date" )
			#	date = datetime.strptime( date_str, '%Y/%m/%d %H:%M:%S' ),

			#	edition = record.find(".//{%s}edition" % DDD_NS).text,
				edition = record_find_text( record, DDD_NS, "edition" ),

				# Not in Lucene results
				#url = record.find( ".//{%s}url" % DDD_NS ).text,
			#	url = record.find( ".//{%s}metadataKey" % DDD_NS ).text,
				url = record_find_text( record, DDD_NS, "metadataKey" ),

			#	type = record.find(".//{%s}type" % DC_NS).text,
				type = record_find_text( record, DC_NS, "type" ),

				# Not in Lucene results
			#	issue = int(record.find(".//{%s}issue" % DDD_NS).text),
			#	issue = record_find_text( record, DDD_NS, "issue" ),
				issue = 0,

			#	spatialCreation = record.find(".//{%s}spatialCreation" % DDD_NS).text,
				spatialCreation = record_find_text( record, DDD_NS, "spatialCreation" ),

				# Not in Lucene results
				#year = int(record.find(".//{%s}year" % DDD_NS).text),
				year = datetime.strptime( record.find( ".//{%s}date" % DC_NS ).text, '%Y/%m/%d %H:%M:%S' ).year,
				# ...

			#	page = int(record.find(".//{%s}page" % DDD_NS).text),
				page = page_num,

			#	ppn = record.find(".//{%s}ppn" % DDD_NS).text,
				ppn = record_find_text( record, DDD_NS, "ppn" ),

			#	source = record.find(".//{%s}source" % DC_NS).text,
				source = record_find_text( record, DC_NS, "source" ),

			#	paperurl = record.find(".//{%s}paperurl" % DDD_NS).text,
				paperurl = record_find_text( record, DDD_NS, "paperurl" ),

			#	pageurl = record.find(".//{%s}pageurl" % DDD_NS).text,
				pageurl = record_find_text( record, DDD_NS, "pageurl" ),

				# Not in Lucene results
				#articleurl = record.find(".//{%s}identifier" % DC_NS).text)
			#	articleurl = record.find(".//{%s}metadataKey" % DDD_NS).text)
				articleurl = record_find_text( record, DDD_NS, "metadataKey" )
			)

		#	article.save()
			# notice: we now truncate the title above to [:255], 
			# because sometimes we got exception warnings with article.save()
			try:
				article.save()
			except:
				type, value, tb = exc_info()
				msg = "article.save() failed: %s" % value.message
				logger.error( msg )
				if settings.DEBUG == True:
					print >> stderr, msg
#				article = DigitaleDagbladenArticle.objects.get(identifier=docID)

		else:
			article = DigitaleDagbladenArticle.objects.get( identifier = docID )

		lexicon = LexiconItem.objects.get( id = lexiconID )
		# Need to add startRecord in Lucene results
		position = startRecord + int( record.find( ".//{%s}recordPosition" % SRW_NS ).text )
		lexiconArticle = LexiconArticle.objects.create( 
			article = article, lexicon = lexicon, position = position )
	except DatabaseError, exc:
		return storeDigitaleDagbladenArticle.retry( exc = exc )
	except DigitaleDagbladenArticle.DoesNotExist, exc:
		return storeDigitaleDagbladenArticle.retry( args = [recordString, docID, lexiconID ], exc = exc )
	except ( IntegrityError, DigitaleDagbladenArticle.MultipleObjectsReturned ), exc:
		DigitaleDagbladenArticle.objects.filter( identifier = docID ).delete()
		return storeDigitaleDagbladenArticle.retry( args = [ recordString, docID, lexiconID ], exc = exc )
#	except AttributeError, exc:
#		if celery_version_maj < 3:
#			logger = storeDigitaleDagbladenArticle.get_logger()
#		else:
#			global logger
#		logger.error("AttributeError in document {%s}" % docID)
#		# return storeDigitaleDagbladenArticle.retry(exc=exc)

# [eof]
