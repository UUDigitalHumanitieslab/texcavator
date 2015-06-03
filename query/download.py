# -*- coding: utf-8 -*-
"""
Query data download (export) functionality.
"""

import os
import datetime
import unicodedata
import base64
import logging
import json
from sys import stderr

from django.conf import settings

from .tasks import zipquerydata

logger = logging.getLogger(__name__)


def create_zipname(user, query):
    """Returns a name for the zipfile containing the exported data.
    """
    date_created = query.date_created.strftime('%Y.%m.%d-%H.%M.%S')
    return '_'.join([user.username, query.title, date_created])


def clean_filename(s):
    """Strips problematic characters from filename
    """
    s = ''.join((c for c in unicodedata.normalize('NFD', s)
                 if unicodedata.category(c) != 'Mn'))
    s = s.replace(' ', '_')
    s = "".join(i for i in s if (i.isalnum() or i == '_'))
    return s


def execute(query, req_dict, zip_basename, to_email, email_message):
    """Expires old data and then compiles the Celery task
    for sending the export via email.
    """
    if settings.DEBUG:
        print >> stderr, "execute()"
    logger.debug("%s: %s" % (__name__, "execute()"))

    if settings.QUERY_DATA_DELETE_DATA:
        expire_data()        # delete old download stuff

    # add the request parameters
    req_dict['zip_basename'] = zip_basename
    req_dict['to_email'] = to_email
    req_dict['email_message'] = email_message
    req_dict.update(query.get_query_dict())
    if settings.DEBUG:
        print >> stderr, req_dict

    # convert to base64
    req_str = json.dumps(req_dict)
    req_base64 = base64.b64encode(req_str)
    if settings.DEBUG:
        print >> stderr, req_base64

    if settings.DEBUG:
        print 'Calling zipquerydata\n'

    task = zipquerydata(req_base64)
    msg = 'management/download/ - Celery task id: {}'.format(task.id)
    logger.info(msg)
    return msg


def expire_data():
    """Deletes old data from the data folder.
    """
    msg = "%s: %s" % (__name__, "expire_data()")
    logger.debug(msg)
    if settings.DEBUG:
        print >> stderr, "expire_data()"

    ddir = settings.QUERY_DATA_DOWNLOAD_PATH
    if settings.DEBUG:
        print >> stderr, "download path:", ddir

    time_now = datetime.datetime.now()        # <type 'datetime.datetime'>
    if settings.DEBUG:
        print >> stderr, "time_now:", time_now

    # Don't try to delete files if folder doesn't exist
    if not os.path.exists(ddir):
        return

    files = os.listdir(ddir)
    files.sort()
    for fname in files:
        if settings.DEBUG:
            print >> stderr, fname
        fpath = os.path.join(ddir, fname)
        if settings.DEBUG:
            print >> stderr, fpath

        time_created_float = os.path.getctime(fpath)
        time_created = datetime.datetime.fromtimestamp(time_created_float)
        if settings.DEBUG:
            print>> stderr, "time_created: %s" % time_created

        elapsed = time_now - time_created
        if settings.DEBUG:
            print>> stderr, "elapsed: %s" % elapsed

        if elapsed.days >= settings.QUERY_DATA_EXPIRE_DAYS:
            msg = "deleting query data file: %s" % fpath
            logger.debug(msg)
            if settings.DEBUG:
                print>> stderr, msg

            try:
                os.remove(fpath)         # DELETING QUERY DATA DOWNLOAD FILE
            except Exception as e:
                msg = "deleting query data file failed: %s" % str(e)
                logger.debug(msg)
                if settings.DEBUG:
                    print >> stderr, msg

        else:
            msg = "keeping query data file: %s" % fpath
            logger.debug(msg)
            if settings.DEBUG:
                print>> stderr, msg
