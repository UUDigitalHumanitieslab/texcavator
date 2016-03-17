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
    """
    Export cloud data to a csv file
    """
    r = request.POST

    content = r.get('clouddata', '')

    zipped_str = r.get('zipped', '0')
    zipped = zipped_str == '1'

    default_filename = 'cloud.csv.zip' if zipped else 'cloud.csv'
    filename = r.get('filename', default_filename)

    separator_str = r.get('separator', 'tab')
    separator = ',' if separator_str == 'comma' else '\t'

    if zipped:
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=' + filename
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + filename

    fout = StringIO.StringIO()  # in-memory temp output file

    writer = csv.writer(fout, delimiter=separator)

    lines = content.split('\n')
    for n, line in enumerate(lines):
        outlist = []
        components = line.split(',')

        if n == 0:
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
        zf.writestr('cloud.csv', fout.getvalue())						# write csv data to zip
        zf.close()
    else:
        response.write(fout.getvalue())								# write data to http response

    return response
