# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		services/export.py
Version:	0.2
Goal:		Export functions

FL-14-Jun-2012: Created
FL-26-Aug-2013: Changed
"""

from sys import stderr
import csv
import StringIO
import zipfile

from django.conf import settings
from django.http import HttpResponse


def export_csv( request ):
#	print >> stderr, "export_cvs()"

	dict = request.REQUEST		# searches POST first, then GET

	try:
		content = dict[ "clouddata" ]
	except( KeyError ):
		content = ""
#	print >> stderr, "content: %s" % content

	try:
		zipped_str = dict[ "zipped" ]
		if zipped_str == '1':
			zipped = True
		else:
			zipped = False
	except( KeyError ):
		zipped = False

	try:
		filename = dict[ "filename" ]
	except( KeyError ):
		if zipped == True:
			filename = "cloud.csv.zip"
		else:
			filename = "cloud.csv"

	try:
		separator_str = dict[ "separator" ]
	except( KeyError ):
		separator_str = "tab"
	if settings.DEBUG == True:
		print >> stderr, "separator: %s" % separator_str
	if separator_str == "comma":
		separator = ','
	else:
		separator = '\t'

	try:
		str_zipped = dict[ "zipped" ]
	except( KeyError ):
		str_zipped = 0
#	print >> stderr, "str_zipped: %s" % str_zipped

	if str_zipped == '1':
		zipped = True
	else:
		zipped = False
#	print >> stderr, "zipped: %s" % zipped

	if zipped:
		response = HttpResponse( mimetype = "application/zip" )
		response[ 'Content-Disposition' ] = 'attachment; filename=' + filename
	else:
		response = HttpResponse( mimetype = "text/csv" )
		response[ 'Content-Disposition' ] = 'attachment; filename=' + filename

	fout = StringIO.StringIO()											# in-memory temp output file

	writer = csv.writer( fout, delimiter = separator )

#	writer.writerow( [ "id", "count", "term", "type" ] )
#	writer.writerow( [ "1", "5", "aap", "PER" ] )
	lines = content.split( '\n' )
	for l in range( len( lines ) ):
		line = lines[ l ]
	#	print >> stderr, line

		outlist = []
		components = line.split( ',' )

		if l == 0:
			ncomp0 = len( components )
		else:
			ncomp = len( components )
			if ncomp != ncomp0:
				if settings.DEBUG == True:
					print >> stderr, line
					print >> stderr, "bad number of components: %d instead of %d" % ( ncomp, ncomp0 )
					print >> stderr, components

		for comp in components:
			# unicode -> utf-8, and strip the '\n' from the last component
			outlist.append( comp.encode( 'utf-8' ).strip() )
	#	print >> stderr, outlist
		writer.writerow( outlist )

	if zipped:
		zf = zipfile.ZipFile( response, 'w', zipfile.ZIP_DEFLATED )		# write zip to http response
		zf.writestr( "cloud.csv", fout.getvalue() )						# write csv data to zip
		zf.close()
	else:
		response.write( fout.getvalue() )								# write data to http response

	return response

# [eof]
