# -*- coding: utf-8 -*-
"""Functionality for exporting cloud data.
"""

from sys import stderr
import csv
import StringIO
import zipfile

from django.conf import settings
from django.http import HttpResponse


def export_csv(request):
    """Export cloud data to a cvs file
    """
    dict = request.REQUEST		# searches POST first, then GET

    try:
        content = dict["clouddata"]
    except(KeyError):
        content = ""

    try:
        zipped_str = dict["zipped"]
        if zipped_str == '1':
            zipped = True
        else:
            zipped = False
    except(KeyError):
        zipped = False

    try:
        filename = dict["filename"]
    except(KeyError):
        if zipped:
            filename = "cloud.csv.zip"
        else:
            filename = "cloud.csv"

    try:
        separator_str = dict["separator"]
    except(KeyError):
        separator_str = "tab"

    if settings.DEBUG:
        print >> stderr, "separator: %s" % separator_str
    if separator_str == "comma":
        separator = ','
    else:
        separator = '\t'

    try:
        str_zipped = dict["zipped"]
    except(KeyError):
        str_zipped = 0

    if str_zipped == '1':
        zipped = True
    else:
        zipped = False

    if zipped:
        response = HttpResponse(mimetype="application/zip")
        response['Content-Disposition'] = 'attachment; filename=' + filename
    else:
        response = HttpResponse(mimetype="text/csv")
        response['Content-Disposition'] = 'attachment; filename=' + filename

    fout = StringIO.StringIO()  # in-memory temp output file

    writer = csv.writer(fout, delimiter=separator)

    lines = content.split('\n')
    for l in range(len(lines)):
        line = lines[l]

        outlist = []
        components = line.split(',')

        if l == 0:
            ncomp0 = len(components)
        else:
            ncomp = len(components)
            if ncomp != ncomp0:
                if settings.DEBUG:
                    print >> stderr, line
                    print >> stderr, "bad number of components: %d instead of %d" % (ncomp, ncomp0)
                    print >> stderr, components

        for comp in components:
            # unicode -> utf-8, and strip the '\n' from the last component
            outlist.append(comp.encode('utf-8').strip())
        writer.writerow(outlist)

    if zipped:
        zf = zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED)		# write zip to http response
        zf.writestr("cloud.csv", fout.getvalue())						# write csv data to zip
        zf.close()
    else:
        response.write(fout.getvalue())								# write data to http response

    return response
