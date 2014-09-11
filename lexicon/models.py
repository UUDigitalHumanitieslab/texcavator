# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Daan Odijk, Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/views.py
Version:	0.2
Goal:		services/views

DO-%%-%%%-2011: Created
FL-28-Aug-2012: DayStatistic table
FL-05-Nov-2012: LexiconWord & StopWord tables
FL-26-Aug-2013: Changed
"""

from django.contrib.auth.models import User
from django.db import models


class DigitaleDagbladenArticle( models.Model ):
	identifier      = models.CharField( max_length = 255, unique = True )
	title           = models.CharField( max_length = 255 )
	papertitle      = models.CharField( max_length = 255 )
	publisher       = models.CharField( max_length = 255 )
	date            = models.DateField()
	edition         = models.CharField( max_length = 50 )
	url             = models.CharField( max_length = 255 )
	type            = models.CharField( max_length = 50 )		# Advertenties, Algemeen bericht, Familiebericht , Illustratie met onderschrift
	issue           = models.IntegerField()
	spatialCreation = models.CharField( max_length = 255 )
	year            = models.IntegerField()
	page            = models.IntegerField()
	ppn             = models.CharField( max_length = 50 )
	source          = models.CharField( max_length = 255 )
	paperurl        = models.CharField( max_length = 255 )
	pageurl         = models.CharField( max_length = 255 )
	articleurl      = models.CharField( max_length = 255 )
	
	def __unicode__(self):
	#	return self.title
		return self.identifier

#     <srw:record>
#       <srw:recordPacking>xml</srw:recordPacking>
#       <srw:recordSchema>http://www.kb.nl/ddd</srw:recordSchema>
#       <srw:recordData>
#         <ddd:accessible>1</ddd:accessible>
#         <ddd:paperurl>http://resolver.kb.nl/resolve?urn=ddd:010001544:mpeg21</ddd:paperurl>
#         <ddd:pageurl>ddd:010001544:mpeg21:p005</ddd:pageurl>
#         <dc:title>BUITENLAND. De Wereld. Papaversap en Politiek.</dc:title>
#         <ddd:papertitle>Het Centrum</ddd:papertitle>
#         <ddd:publisher>M&#307;. tot Exploitatie v/h Dagblad Het Centrum</ddd:publisher>
#         <dc:date>1925/01/22 00:00:00</dc:date>
#         <ddd:edition>Dag</ddd:edition>
#         <ddd:ppn>832369047</ddd:ppn>
#         <ddd:url>http://resources2.kb.nl/010000000/articletext/010001544/DDD_010001544_0061_articletext.xml</ddd:url>
#         <dc:type>artikel</dc:type>
#         <ddd:issue>0</ddd:issue>
#         <ddd:spatialCreation>Utrecht</ddd:spatialCreation>
#         <ddd:year>1925</ddd:year>
#         <ddd:page>5</ddd:page>
#         <ddd:vdkvgwkey>http://resolver.kb.nl/resolve?urn=ddd:010001544:mpeg21:a0061:ocr</ddd:vdkvgwkey>
#         <dc:identifier>http://resolver.kb.nl/resolve?urn=ddd:010001544:mpeg21:a0061:ocr</dc:identifier>
#         <dc:source>KB NBM Mfm MMK 0024 [Microfilm]</dc:source>
#       </srw:recordData>
#       <srw:recordPosition>20</srw:recordPosition>
#     </srw:record>


class LexiconItem( models.Model ):
	user      = models.CharField( max_length =  50, blank = True )	# to limit visibility of lexicons
	group     = models.CharField( max_length =  50, blank = True )	# to limit visibility of lexicons
	title     = models.CharField( max_length = 200 )
	query     = models.TextField()
	created   = models.DateTimeField( 'date created', auto_now = True )
	documents = models.ManyToManyField( DigitaleDagbladenArticle, through = 'LexiconArticle' )
	
	def __unicode__( self ):
		return self.title


class LexiconArticle( models.Model ):
	lexicon  = models.ForeignKey( LexiconItem )
	article  = models.ForeignKey( DigitaleDagbladenArticle )
	position = models.IntegerField()

	def __unicode__( self ):
		return self.lexicon.title


class LexiconWord( models.Model ):
	user    = models.CharField( max_length =  50, blank = True )
	word    = models.CharField( max_length = 100, db_index = True )
#	created = models.DateTimeField( 'date created', auto_now = True )

	def __unicode__( self ):
		return self.word


class StopWordOld( models.Model ):
	user    = models.ForeignKey( User, null = True )
	query   = models.ForeignKey( LexiconItem, null = True )
	word    = models.CharField( max_length = 100, db_index = True )
#	created = models.DateTimeField( 'date created', auto_now = True )

	def __unicode__( self ):
		return self.word


# For Daan's Timeline graph
# The table is filled with the 'gatherstatistics' management command
class DayStatistic( models.Model ):
	date    = models.DateField( unique = True )
	count   = models.IntegerField()
	checked = models.DateTimeField( auto_now = True )

	def __unicode__( self ):
		from datetime import datetime 
		return "%d%02d%02d: %d" % ( self.date.year, self.date.month, self.date.day, self.count )

# [eof]
