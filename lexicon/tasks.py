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
	addLexiconItemToXtas( lexiconID, datastore, begindate, enddate )
		call addSRUResultsToXtas() in chunks (of 50)
	addSRUResultsToXtas( query, lexiconID, startRecord = 1, maximumRecords = 20 )
		for record in chunk: 
			obtain document metadata metadata by KB SRU request
			call storeDigitaleDagbladenArticle()
			call addResolverDocumentToXtas()
	storeDigitaleDagbladenArticle( recordString, docID, lexiconID, startRecord, storeRecord = True )
		extract document metadata -> Django MySQL
	addResolverDocumentToXtas( docID, lexiconID )
		obtain document OCR XML fom KB resolver, and store in xTAS
"""

import os
from sys import stderr, exc_info
import json

from django.conf import settings
from django.http import HttpResponse

from celery.decorators import task
from celery import __version__ as celery__version__

#from BiLand.lexicon.download import get_es_chunk		# circular import problem?
#from BiLand.services.cql2es import cql2es_error, callperl
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



@task()
def addLexiconItemToXtas( lexiconID, datastore, collection, begindate, enddate ):
	"""call addSRUResultsToXtas() in chunks"""
	global logger
	if celery_version_maj < 3:
		logger = addLexiconItemToXtas.get_logger()
#	print >> stderr, "tasks.py/addLexiconItemToXtas()"

	from lexicon.models import LexiconItem, LexiconArticle
	from lxml import etree
	from django.db import DatabaseError

	try:
		li = LexiconItem.objects.get( pk = lexiconID )

		# Delete existing items referring to this lexicon		
		LexiconArticle.objects.filter( lexicon = lexiconID ).delete()
	except LexiconItem.DoesNotExist:
		msg = "Lexicon with id %s cannot be found." % lexiconID
		logger.error( msg )
		if settings.DEBUG == True:
			print >> stderr, msg
		return
	except DatabaseError, exc:
		return addLexiconItemToXtas.retry( exc = exc )

	if datastore == "DSTORE_ELASTICSEARCH":
		msg = "Calling ElasticSearch"
		logger.error( msg )
		if settings.DEBUG == True:
			print >> stderr, msg

		resp_dict = addtags_elasticsearch( lexiconID, collection, begindate, enddate )
	#	return json.dumps( resp_dict )	# Celery creates response object
		return  resp_dict[ "hits_total" ]


	msg = "Adding Lexicon #%s named %s to xTas: %s" % ( lexiconID, li.title, li.query )
	logger.info( msg )
	if settings.DEBUG == True:
		print >> stderr, msg

	start = 1
	step = 50
	msg = "step size: %d" % step
	logger.info( msg )
	if settings.DEBUG == True:
		print >> stderr, msg

	while True:
		msg = "start: %d" % start
		logger.info( msg )
		if settings.DEBUG == True:
			print >> stderr, "\n", msg

	#	numberOfRecords, startRecord, stopRecord = addSRUResultsToXtas.delay( datastore, li.query, lexiconID, start, step ).get()
		numberOfRecords, startRecord, stopRecord = addSRUResultsToXtas.delay( datastore, begindate, enddate, li.query, lexiconID, start, step ).get()

		"""
		result = addSRUResultsToXtas.delay( datastore, li.query, lexiconID, start, step )
		msg = "addSRUResultsToXtas.delay()"
		logger.info( msg )
		if settings.DEBUG == True:
			print >> stderr, "\n", msg
		numberOfRecords, startRecord, stopRecord = result.get()
		"""

		addLexiconItemToXtas.update_state( state = "PROGRESS", 
			meta = { "start": start, "step": step, "total": numberOfRecords, 
				"currentPage": int( start/step ) + 1, "totalPages": int( numberOfRecords/step ) + 1 } )

		start = stopRecord + 1		# new start
		if start > numberOfRecords:
			break

	return numberOfRecords
	# Check if all SRU done, then remove unneeded docs?
	# return



#@task( rate_limit = "10/s" )
@task
def addSRUResultsToXtas( datastore, begindate, enddate, query, lexiconID, startRecord = 1, maximumRecords = 20 ):
	"""
	for record in chunk: 
		obtain document metadata metadata by KB SRU request
		call storeDigitaleDagbladenArticle()
		call addResolverDocumentToXtas()\
	"""
	global logger
	if celery_version_maj < 3:
		logger = addSRUResultsToXtas.get_logger()
#	print >> stderr, "tasks.py/addSRUResultsToXtas()"

	msg = "Adding SRU results to xTas for query: %s [start: %d, max: %d]" % ( query, startRecord, maximumRecords )
	logger.info( msg )
	if settings.DEBUG == True:
		print >> stderr, msg

	from lxml import etree
	from services.views import proxyResponse, SRU_QUERY
	from socket import error, herror, gaierror

	# Set defaults for SRU search options
	data = {'operation': 'searchRetrieve', 'version': '1.2', 'recordSchema':'ddd',
			'x-collection': 'DDD_artikel', 'x-fields': 'abstract'}
	data[ 'query' ] = query
	data[ 'startRecord' ] = startRecord
	data[ 'maximumRecords' ] = maximumRecords

	# Update the query to enforce the date range
#	data[ 'query' ] = SRU_QUERY % ( query, SRU_DATE_LIMITS[ 0 ], SRU_DATE_LIMITS[ 1 ] )
	data[ 'query' ] = SRU_QUERY % ( query, int(begindate), int(enddate) )

	msg = "KB SRU request: %s" % data[ 'query' ]
	logger.info( msg )
	if settings.DEBUG == True:
		print >> stderr, msg

	# Get the proxied httplib HTTPResponse
	try:
		result = proxyResponse( 'GET', 'jsru.kb.nl', 80, 'sru/sru.pl', data )
	except( error, herror, gaierror ), exc:
		type, value, tb = exc_info()
		logger.info( value.message )
		if settings.DEBUG == True:
			print >> stderr, value.message
		return addSRUResultsToXtas.retry( exc = exc )

	result_str = result.read()
	doc = etree.fromstring( result_str )		# parse xml string to etree object

#	logger.info( etree.fromstring( result_str ) )
#	if settings.DEBUG == True:
#		print >> stderr, "result_str: ", result_str

	# numberOfRecords is the total # available, not just the number of the chunk requested
	numberOfRecords = int( doc.find( ".//{%s}numberOfRecords" % SRW_NS ).text )
	records = doc.findall( ".//{%s}record" % SRW_NS )
	#addResolverDocumentToXtasSubtask = addResolverDocumentToXtas.subtask( args=(lexiconID) )

	docIDs = []
	Nremoved = 0
	Nappended = 0
	for record in records:
		identifier  = record.find( ".//{%s}identifier"  % DC_NS  ).text.split("=")[1]	# ends width ':ocr'
		metadataKey = record.find( ".//{%s}metadataKey" % DDD_NS ).text.split("=")[1]	# does not end width ':ocr'

		# apart from the ':ocr' ending, these 2 are the same
		if settings.XTAS_DOC_ID == "IDENTIFIER":
			docID = identifier					# old: used by Daan
		elif settings.XTAS_DOC_ID == "METADATAKEY":
			docID = metadataKey					# new: used by Ridho
		else:
			docID = None

		if docID == None:
			records.remove( record )
			Nremoved += 1
		else:
			docIDs.append( docID )
			Nappended += 1

	if settings.DEBUG == True:
		print >> stderr, "removed: %d records" % Nremoved
		print >> stderr, "appended: %d records" % Nappended

	from models import DigitaleDagbladenArticle
	from django.db import DatabaseError

	try:
		existingRecords = DigitaleDagbladenArticle.objects.filter( identifier__in=docIDs ).only( "identifier" )
	except DatabaseError, exc:
		return addSRUResultsToXtas.retry( exc = exc )
	existingDocs = [ rec.identifier for rec in existingRecords ]

	for record in records:
		# Add record to local DB if needed
		# Only if not already in local DB?
		docID = docIDs[ records.index( record ) ]
		# Need to send startRecord too, as position is from startRecord
		if docID in existingDocs:
			storeDigitaleDagbladenArticle.delay( etree.tostring( record ), docID, lexiconID, startRecord, False )
		else:
			storeDigitaleDagbladenArticle.delay( etree.tostring( record ), docID, lexiconID, startRecord )
			#addResolverDocumentToXtasSubtask.delay(docID)

		addResolverDocumentToXtas.delay( datastore, docID, lexiconID )

	if len( records ) == 0:
	#	return [ numberOfRecords, startRecord if numberOfRecords else 0, startRecord if numberOfRecords else 0 ]
		return numberOfRecords, startRecord if numberOfRecords else 0, startRecord if numberOfRecords else 0
	else:
#		Not working anymore, because Lucene starts counting from 0, no matter what.
# 		return [numberOfRecords, 
# 				int(records[0].find(".//{%s}recordPosition" % SRW_NS).text),
# 				int(records[-1].find(".//{%s}recordPosition" % SRW_NS).text)]
		recordPosition = int( records[ -1 ].find(".//{%s}recordPosition" % SRW_NS ).text )
	#	stopRecord = startRecord + recordPosition	# relative recordPosition
		stopRecord = recordPosition					# absolute recordPosition
	#	return [ numberOfRecords, startRecord, stopRecord ]
		return numberOfRecords, startRecord, stopRecord



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



#@task( rate_limit = "10/s" )
@task
def addResolverDocumentToXtas( datastore, docID, lexiconID ):
	"""obtain document OCR XML fom KB resolver, and store in xTAS"""
	global logger
	if celery_version_maj < 3:
		logger = addResolverDocumentToXtas.get_logger()
#	print >> stderr, "tasks.py/addResolverDocumentToXtas()"

	if datastore == "DSTORE_ELASTICSEARCH":
		if docID.endswith( ":ocr" ):
			docID = docID[ :-4 ]		# strip ":ocr"
		msg = "Adding document %s from lexicon #%s to xTAS (ElasticSearch)" % ( docID, lexiconID )
	else:
		msg = "Adding document %s from lexicon #%s to xTAS (MongoDB)" % ( docID, lexiconID )

	logger.info( msg )
	if settings.DEBUG == True:
		print >> stderr, msg

	from socket import error, herror, gaierror
	from settings import XTAS_HOST, XTAS_PORT, XTAS_PREFIX, XTAS_API_KEY
	from services.views import proxyResponse

	# cache documentIDs and metadata
	# flag for overwrite
	# apply tag Lexicon#

	if XTAS_PREFIX == '':
		xtas_path = ''
	else:
		xtas_path = XTAS_PREFIX + '/'
	xtas_path += 'doc/addtags'
	tags = "ddd,Lexicon%s" % lexiconID

	try:
		data = { "ids": docID, "tags": tags, "key": XTAS_API_KEY }
		result = proxyResponse( 'POST', XTAS_HOST, XTAS_PORT, xtas_path, data )

		doc = result.read()
		if doc.find( docID ) != -1:
			msg = "Document %s already in xTAS" % docID
			logger.warning( msg )
			if settings.DEBUG == True:
				print >> stderr, msg
			return doc
	except (error, herror, gaierror), exc:
		return addResolverDocumentToXtas.retry( exc = exc )

	if datastore == "elasticsearch":
		return		# OCR preloaded


	msg = "Sending document %s to xTAS." % docID
	logger.info( msg )
	if settings.DEBUG == True:
		print >> stderr, msg

	try:
		result = proxyResponse( 'GET', 'resolver.kb.nl', 80, 'resolve', { "urn": docID } )
	except (error, herror, gaierror), exc:
		return addResolverDocumentToXtas.retry( exc = exc )

	from re import compile
	tagPattern = compile( r"<.*?>" )
	doc = result.read()
	doc = doc.replace( "&lt;", "<" ).replace( "&gt;", ">" ).replace( "&amp;", "&" )
	doc = tagPattern.sub( "", doc ).strip()
#	if settings.DEBUG == True:
#		print >> stderr, doc[0:200]
	
	metadata = json.dumps( { "language": "nl" } )
	data = { "id": docID, "metadata": metadata, "replace": 1, "document": doc, "key": XTAS_API_KEY }
	data[ "tags" ] = "ddd,Lexicon%s" % lexiconID

	try:
		if settings.DEBUG == True:
			print >> stderr, XTAS_HOST
		if XTAS_PREFIX == '':
			xtas_path = 'doc'
		else:
			xtas_path = XTAS_PREFIX + '/' + 'doc'
		result = proxyResponse( 'POST', XTAS_HOST, XTAS_PORT, xtas_path, data )
	except (error, herror, gaierror), exc:
		return addResolverDocumentToXtas.retry( exc = exc )
	output = result.read()
	if settings.DEBUG == True:
		print output
	logger.info( output )
	return output


# Old Verity example response
# <srw:record>
# 	<srw:recordPacking>xml</srw:recordPacking>
# 	<srw:recordSchema>http://www.kb.nl/ddd</srw:recordSchema>
# 	<srw:recordData>
# 		<ddd:accessible>1</ddd:accessible>
# 		<ddd:paperurl>http://resolver.kb.nl/resolve?urn=ddd:010015649:mpeg21</ddd:paperurl>
# 		<ddd:pageurl>ddd:010015649:mpeg21:p002</ddd:pageurl>
# 		<dc:title>INTERNAT. BENDE VAN OPIUMSMOKKELAARS ONTMASKERD Een wijd vertakte bende, met vele chineezen, Grieken en a.s. ook een inspecteur van politie als leden</dc:title>
# 		<ddd:papertitle>Het Vaderland : staat- en letterkundig nieuwsblad</ddd:papertitle>
# 		<ddd:publisher>M. Nĳhoff [etc.]</ddd:publisher>
# 		<dc:date>1934/11/03 00:00:00</dc:date>
# 		<ddd:alternative>Het Vaderland</ddd:alternative>
# 		<ddd:edition>Avond</ddd:edition>
# 		<ddd:ppn>832689858</ddd:ppn>
# 		<ddd:url>http://resources2.kb.nl/010015000/articletext/010015649/DDD_010015649_0021_articletext.xml</ddd:url>
# 		<dc:type>artikel</dc:type>
# 		<ddd:issue>0</ddd:issue>
# 		<ddd:spatialCreation>'s-Gravenhage</ddd:spatialCreation>
# 		<ddd:year>1934</ddd:year>
# 		<ddd:page>2</ddd:page>
# 		<ddd:vdkvgwkey>http://resolver.kb.nl/resolve?urn=ddd:010015649:mpeg21:a0021:ocr</ddd:vdkvgwkey>
# 		<dc:identifier>http://resolver.kb.nl/resolve?urn=ddd:010015649:mpeg21:a0021:ocr</dc:identifier>
# 		<dc:source>KB NBM C 44 [Microfilm]</dc:source>
# 	</srw:recordData>
# 	<srw:recordPosition>1</srw:recordPosition>
# </srw:record>
# 
# New Lucene example response
# 	<srw:record>
# 		<srw:recordPacking>xml</srw:recordPacking>
# 		<srw:recordSchema>http://www.kb.nl/ddd</srw:recordSchema>
# 		<srw:recordData>
# 			<ddd:metadataKey>http://resolver.kb.nl/resolve?urn=ddd:010013335:mpeg21:a0295</ddd:metadataKey>
# 			<dc:type>artikel</dc:type>
# 			<ddd:spatial>Landelijk</ddd:spatial>
# 			<ddd:page>1</ddd:page>
# 			<ddd:edition>Dag</ddd:edition>
# 			<ddd:pageurl>ddd:010013335:mpeg21:p013</ddd:pageurl>
# 			<ddd:paperurl>http://resolver.kb.nl/resolve?urn=ddd:010013335:mpeg21</ddd:paperurl>
# 			<ddd:yearsdigitized>1920-1945</ddd:yearsdigitized>
# 			<ddd:alternative>Het Vaderland</ddd:alternative>
# 			<ddd:publisher>M. Nĳhoff [etc.]</ddd:publisher>
# 			<dc:source>KB NBM C 44 [Microfilm]</dc:source>
# 			<ddd:ppn>832689858</ddd:ppn>
# 			<ddd:accessible>1</ddd:accessible>
# 			<ddd:papertitle>Het Vaderland : staat- en letterkundig nieuwsblad</ddd:papertitle>
# 			<dc:date>1931/02/01 00:00:00</dc:date>
# 			<ddd:issued>1869-1945</ddd:issued>
# 			<ddd:spatialCreation>'s-Gravenhage</ddd:spatialCreation>
# 			<dc:title>OPIUM</dc:title>
# 		</srw:recordData>
# 		<srw:recordPosition>0</srw:recordPosition>
# 	</srw:record>

"""
@task
def task_download_collect( req_dict, zip_basename ):
#	Actual creation/collection of document files
	if settings.DEBUG == True:
		print >> stderr, "task_download_collect()"
		logger.debug( "task_download_collect()" )

	query_str, literal, date_begin, date_end, start_record, chunk_size, collection = request2parms( req_dict )

	# download format: JSON or XML
	try:
		format = req_dict[ "format" ]
	except:
		format = "json"
	if settings.DEBUG == True:
		print >> stderr, "format", format

	# Add the KB document type[s] selection to the query
	doc_types = request2article_types( req_dict )
	if settings.DEBUG == True:
		print >> stderr, "type_query", doc_types
	if collection == settings.ES_INDEX_KONBIB and doc_types is not None:
		query_str += doc_types

	# Add the date range
	query_str += " AND (paper_dc_date >= " + date_begin + " AND paper_dc_date <= " + date_end + ")"

	if settings.DEBUG == True:
		print >> stderr, "query_str:", query_str

	try:
		es_query_str = callperl( query_str, literal )	# call Perl: CQL -> ES JSON
	except:
		type, value, tb = exc_info()
		return cql2es_error( value )

	if settings.DEBUG == True:
		print >> stderr, "es_query: %s" % es_query_str

	# just get the hit count
	start_record = 0
	chunk_1_size = 1
	hits, resp_object = get_es_chunk( es_query_str, start_record, chunk_1_size )

	if resp_object is not None:
		return resp_object

	zip_basedir  = os.path.join( settings.PROJECT_PARENT, settings.QUERY_DATA_DOWNLOAD )
	zip_filename = zip_basename + ".zip"
	zip_pathname = os.path.join( zip_basedir, zip_filename )

	# create zipfile
	try:
		zip_file = zipfile.ZipFile( zip_pathname, mode = 'w', compression = zipfile.ZIP_DEFLATED )
	except:
		type, value, tb = exc_info()
		msg = "opening OCR file failed: %s" % value
		if settings.DEBUG == True:
			print >> stderr, msg
		resp_dict = { "status" : "error", "msg" : msg }
		json_list = json.dumps( resp_dict )
		ctype = 'application/json; charset=UTF-8'
		return HttpResponse( json_list, content_type = ctype )

	# how many chunks do we need?
	from math import ceil
	chunk_size = 500
	hits_total = hits[ "total" ]
	nchunks = int( ceil( float( hits_total ) / float( chunk_size ) ) )
	hits_zipped = 0

	for ichunk in range( nchunks ):
		start_record = ichunk * chunk_size
		nchunk = ichunk + 1

		if settings.DEBUG == True:
			print >> stderr, "nchunk:", nchunk, "of", nchunks, "start_record:", start_record

		hits, resp_object = get_es_chunk( es_query_str, start_record, chunk_size )

		hits_list = hits[ "hits" ]
		hits_zipped += len( hits_list )
		zip_chunk( hits_list, zip_file )

	if settings.DEBUG == True:
		print >> stderr, "hits_zipped:", hits_zipped
	"""

# [eof]
