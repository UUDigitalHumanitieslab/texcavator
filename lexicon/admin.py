# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Daan Odijk, Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		lexicon/views.py
Version:	0.4
Goal:		services/views

DO-%%-%%%-2011: Created
FL-28-Aug-2012: DayStatistic added
FL-26-Nov-2012: LexiconWord, StopWord added
FL-26-Aug-2013: Changed
"""


from lexicon.models import LexiconItem, LexiconArticle, DigitaleDagbladenArticle, LexiconWord, StopWord, DayStatistic
from django.contrib import admin

class LexiconItemAdmin( admin.ModelAdmin ):
	list_display = ( 'id', 'user', 'group', 'created', 'title' )

class LexiconArticleAdmin( admin.ModelAdmin ):
	list_display = ( 'lexicon', 'position', 'article' )

class DigitaleDagbladenArticleAdmin( admin.ModelAdmin ):
	list_display = ( 'identifier', 'title' )

class LexiconWordAdmin( admin.ModelAdmin ):
	list_display = ( 'user', 'word' )

class StopWordAdmin( admin.ModelAdmin ):
	list_display = ( 'user', 'query', 'word' )

class DayStatisticAdmin( admin.ModelAdmin ):
	list_display = ( 'date', 'count', 'checked' )


admin.site.register( LexiconItem, LexiconItemAdmin )
admin.site.register( LexiconArticle, LexiconArticleAdmin )
admin.site.register( DigitaleDagbladenArticle, DigitaleDagbladenArticleAdmin )
admin.site.register( LexiconWord, LexiconWordAdmin )
admin.site.register( StopWord, StopWordAdmin )
admin.site.register( DayStatistic, DayStatisticAdmin )

# [eof]
