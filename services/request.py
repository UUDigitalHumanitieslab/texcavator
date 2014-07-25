# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		services/req2arttypes.py
Version:	0.1
Goal:		filter by article type

def request2article_types( request )
def request2article_distrib( reqdict )
def request2parms( req_dict )
def is_literal( query_str )

FL-31-May-2013: Created
FL-13-Dec-2013: Changed
"""

from sys import stderr, exc_info

from django.conf import settings


def request2article_types( reqdict ):
	print >> stderr, "request2article_types()", reqdict

	if reqdict.has_key( "st_article" ):
		st_article_str = reqdict[ "st_article" ]
		if st_article_str == "true":
			st_article = True
		else:
			st_article = False
		if st_article_str == "false":
			st_article = False
		else:
			st_article = True
	else:
		st_article = True

	if reqdict.has_key( "st_advert" ):
		st_advert_str = reqdict[ "st_advert" ]
		if st_advert_str == "true":
			st_advert = True
		else:
			st_advert = False
		if st_advert_str == "false":
			st_advert = False
		else:
			st_advert = True
	else:
		st_advert = True

	if reqdict.has_key( "st_illust" ):
		st_illust_str = reqdict[ "st_illust" ]
		if st_illust_str == "true":
			st_illust = True
		else:
			st_illust = False
		if st_illust_str == "false":
			st_illust = False
		else:
			st_illust = True
	else:
		st_illust = True

	if reqdict.has_key( "st_family" ):
		st_family_str = reqdict[ "st_family" ]
		if st_family_str == "true":
			st_family = True
		else:
			st_family = False
		if st_family_str == "false":
			st_family = False
		else:
			st_family = True
	else:
		st_family = True

#	print >> stderr, "st_article:",st_article 
#	print >> stderr, "st_advert:", st_advert
#	print >> stderr, "st_illust:", st_illust
#	print >> stderr, "st_family:", st_family

	# we only deal with True
	st_count = 0
	if st_article == True: st_count += 1
	if st_advert  == True: st_count += 1
	if st_illust  == True: st_count += 1
	if st_family  == True: st_count += 1
#	print >> stderr, "st_count:", st_count

#	dc_type = "dc.type"					# KB SRU
	dc_type = "article_dc_subject"		# used by Ridho for ES

	if st_count == 4:
		type_query = None	# all 4 True; need not specify dc.type

	elif st_count == 1:
		if st_article == True:
		#	type_query = " AND dc.type=artikel"
			type_query = " AND " + dc_type + "=artikel"

		if st_advert  == True:
		#	type_query = " AND dc.type=advertentie"
			type_query = " AND " + dc_type + "=advertentie"

		if st_illust  == True:
		#	type_query = " NOT (dc.type=artikel OR dc.type=advertentie OR dc.type=familiebericht)"
		#	type_query = ' AND (dc.type="illustratie met onderschrift")'	# "''" does not work
			type_query = ' AND (' + dc_type + '="illustratie met onderschrift")'

		if st_family  == True:
		#	type_query = " AND dc.type=familiebericht"
			type_query = " AND " + dc_type + "=familiebericht"

	else:
		type_query = ""

		if st_article == True:
		#	type_query = "dc.type=artikel"
			type_query = dc_type + "=artikel"

		if st_advert  == True:
			if type_query == "":
			#	type_query = "dc.type=advertentie"
				type_query = dc_type + "=advertentie"
			else:
			#	type_query += " OR dc.type=advertentie"
				type_query += " OR " + dc_type + "=advertentie"

		if st_illust  == True:
			if type_query == "":
			#	type_query = 'dc.type="illustratie met onderschrift"'		# "''" does not work
				type_query = dc_type + '="illustratie met onderschrift"'
			else:
			#	type_query += ' OR dc.type="illustratie met onderschrift"'	# "''" does not work
				type_query += ' OR ' + dc_type + '="illustratie met onderschrift"'

		if st_family  == True:
			if type_query == "":
			#	type_query = "dc.type=familiebericht"
				type_query = dc_type + "=familiebericht"
			else:
			#	type_query += " OR dc.type=familiebericht"
				type_query += " OR " + dc_type + "=familiebericht"

		type_query = " AND (" + type_query + ")"

	return type_query



def request2article_distrib( reqdict ):
	print >> stderr, "request2article_distrib()", reqdict

	if reqdict.has_key( "sd_national" ):
		sd_national_str = reqdict[ "sd_national" ]
		if sd_national_str == "true":
			sd_national = True
		else:
			sd_national = False
		if sd_national_str == "false":
			sd_national = False
		else:
			sd_national = True
	else:
		sd_national = True

	if reqdict.has_key( "sd_regional" ):
		sd_regional_str = reqdict[ "sd_regional" ]
		if sd_regional_str == "true":
			sd_regional = True
		else:
			sd_regional = False
		if sd_regional_str == "false":
			sd_regional = False
		else:
			sd_regional = True
	else:
		sd_regional = True

	if reqdict.has_key( "sd_antilles" ):
		sd_antilles_str = reqdict[ "sd_antilles" ]
		if sd_antilles_str == "true":
			sd_antilles = True
		else:
			sd_antilles = False
		if sd_antilles_str == "false":
			sd_antilles = False
		else:
			sd_antilles = True
	else:
		sd_antilles = True

	if reqdict.has_key( "sd_surinam" ):
		sd_surinam_str = reqdict[ "sd_surinam" ]
		if sd_surinam_str == "true":
			sd_surinam = True
		else:
			sd_surinam = False
		if sd_surinam_str == "false":
			sd_surinam = False
		else:
			sd_surinam = True
	else:
		sd_surinam = True

	if reqdict.has_key( "sd_indonesia" ):
		sd_indonesia_str = reqdict[ "sd_indonesia" ]
		if sd_indonesia_str == "true":
			sd_indonesia = True
		else:
			sd_indonesia = False
		if sd_indonesia_str == "false":
			sd_indonesia = False
		else:
			sd_indonesia = True
	else:
		sd_indonesia = True

	print >> stderr, "sd_national:",  sd_national
	print >> stderr, "sd_regional:",  sd_regional
	print >> stderr, "sd_antilles:",  sd_antilles
	print >> stderr, "sd_surinam:",   sd_surinam
	print >> stderr, "sd_indonesia:", sd_indonesia

	# we only deal with True
	sd_count = 0
	if sd_national  == True: sd_count += 1
	if sd_regional  == True: sd_count += 1
	if sd_antilles  == True: sd_count += 1
	if sd_surinam   == True: sd_count += 1
	if sd_indonesia == True: sd_count += 1
	print >> stderr, "sd_count:", sd_count

#	ddd_spatial = "dcterms.spatial"				# KB SRU
	ddd_spatial = "paper_dcterms_spatial"		# used by Ridho for ES

	national_ustr = u"Landelijk"
	regional_ustr = u"Regionaal/lokaal"
	antilles_ustr = u"Nederlandse Antillen"
	surinam_ustr = u"Suriname"
#	indonesia_ustr = u"Nederlands-Indië / Indonesië"
	indonesia_ustr = u"Indonesië"		# dev server OK, but apache sucks ?!

	if sd_count == 5:
		distrib_query = None	# all 5 True; need not specify dcterms.spatial

	elif sd_count == 1:
		if sd_national    == True:	u_str = national_ustr
		elif sd_regional  == True:	u_str = regional_ustr
		elif sd_antilles  == True:	u_str = antilles_ustr
		elif sd_surinam   == True:	u_str = surinam_ustr
		elif sd_indonesia == True:	u_str = indonesia_ustr

		distrib_query = ' AND (' + ddd_spatial + '="' + u_str + '")'

	else:
		distrib_query = ""

		if sd_national == True:
			distrib_query = ddd_spatial + '="' + national_ustr + '"'

		if sd_regional  == True:
			if distrib_query == "":
				distrib_query = ddd_spatial + '="' + regional_ustr + '"'
			else:
				distrib_query += ' OR ' + ddd_spatial + '="' + regional_ustr + '"'

		if sd_antilles  == True:
			if distrib_query == "":
				distrib_query = ddd_spatial + '="' + antilles_ustr + '"'
			else:
				distrib_query += ' OR ' + ddd_spatial + '="' + antilles_ustr + '"'

		if sd_surinam  == True:
			if distrib_query == "":
				distrib_query = ddd_spatial + '="' + surinam_ustr + '"'
			else:
				distrib_query += ' OR ' + ddd_spatial + '="' + surinam_ustr + '"'

		if sd_indonesia  == True:
			if distrib_query == "":
				distrib_query = ddd_spatial + '="' + indonesia_ustr + '"'
			else:
				distrib_query += ' OR ' + ddd_spatial + '="' + indonesia_ustr + '"'

		distrib_query = " AND (" + distrib_query + ")"

	return distrib_query



def request2parms( req_dict ):
	if settings.DEBUG == True:
		print >> stderr, "request2parms()"
		print >> stderr, req_dict

	# basic query string
	try:
		query_str = req_dict[ "query" ]
	except:
		query_str = ""
	if settings.DEBUG == True:
		print >> stderr, "query_str:", query_str.encode( "utf-8" )

	literal = is_literal( query_str )

	# date range
	try:
		dateRange_str = req_dict[ "dateRange" ]
		dateRange  = dateRange_str.split( ',' )
		date0 = dateRange[ 0 ]
		date1 = dateRange[ 1 ]

		date_begin = "%s-%s-%s" % ( date0[0:4], date0[4:6], date0[6:8] )	# YYYYMMDD -> YYYY-MM-DD
		date_end   = "%s-%s-%s" % ( date1[0:4], date1[4:6], date1[6:8] )	# YYYYMMDD -> YYYY-MM-DD
	except:
		date_begin = None
		date_end   = None

	# start record
	try:
		startRecord = int( req_dict[ "startRecord" ] )
		if startRecord > 1:
			start_record = -1 + startRecord		# KB default 1 -> ES default 0
		else:
			start_record = 0
	except:
		start_record = 0		# not supplied

	# chunk size
	try:
		chunk_size = int( req_dict[ "maximumRecords" ] )
	except:
		chunk_size = 20			# not supplied

	# collection
	try:
		collection = req_dict[ "collection" ]
	except:
		collection = settings.ES_INDEX

	return query_str, literal, date_begin, date_end, start_record, chunk_size, collection


def is_literal( query_str ):
	try:
		query_str.index( "'" )
		squotes = True
	except:
		squotes = False

	try:
		query_str.index( '"' )
		dquotes = True
	except:
		dquotes = False

	if squotes == True  or dquotes == True:
		literal = True
	else:
		literal = False
	if settings.DEBUG == True:
		print >> stderr, "literal:", literal

	return literal

# [eof]
