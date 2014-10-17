# -*- coding: utf-8 -*-
"""
Query data download (export) functionality.
"""

import os
from sys import stderr, exc_info
import csv
from time import strftime
import datetime
import unicodedata
import zipfile
from dicttoxml import dicttoxml

import base64
import subprocess

import logging
logger = logging.getLogger(__name__)

import json

from django.conf import settings
from django.core.mail import send_mail
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from services.es import do_search, daterange2dates, get_search_parameters


def create_zipname(username, query_title):
    query_title_ = username + '_' + query_title
    query_title_ = clean_filename(query_title_)
    zip_basename = query_title_ + "_" + strftime("%Y.%m.%d-%H.%M.%S")

    return zip_basename


def download_collect(req_dict, zip_basename, to_email, email_message):
    """ Actual creation/collection of document files.
    """
    msg = "%s: %s" % (__name__, "download_collect()")
    logger.debug(msg)
    if settings.DEBUG:
        print >> stderr, msg

    # download format: JSON or XML
    try:
        format = req_dict["format"]
    except:
        format = "json"
    if settings.DEBUG:
        print >> stderr, "format", format

    params = get_search_parameters(req_dict)
    es_query_str = params['query']

    msg = "es_query: %s" % es_query_str
    logger.debug(msg)

    # just get the hit count
    start_record = 0
    chunk_1_size = 1
    hits, resp_object = get_es_chunk(params, start_record, chunk_1_size)

    zip_basedir = settings.QUERY_DATA_DOWNLOAD_PATH
    zip_filename = zip_basename + ".zip"
    zip_pathname = os.path.join(zip_basedir, zip_filename)

    logger.debug(zip_pathname)
    if settings.DEBUG:
        print >> stderr, zip_pathname

    # create zipfile
    try:
        zip_file = zipfile.ZipFile(zip_pathname,
                                   mode='w',
                                   compression=zipfile.ZIP_DEFLATED)
    except Exception as e:
        msg = "opening OCR file failed: {}".format(str(e))
        if settings.DEBUG:
            print >> stderr, msg
        resp_dict = {"status": "error", "msg": msg}
        json_list = json.dumps(resp_dict)
        ctype = 'application/json; charset=UTF-8'
        return HttpResponse(json_list, content_type=ctype)

    # how many chunks do we need?
    from math import ceil
    chunk_size = settings.QUERY_DATA_CHUNK_SIZE
    hits_total = hits["total"]
    nchunks = int(ceil(float(hits_total) / float(chunk_size)))
    hits_zipped = 0

    csv_writer = None
    if format == "csv":
        csv_filename = zip_basename + ".csv"
        csv_pathname = os.path.join(zip_basedir, csv_filename)
        # create csv file
        try:
            csv_file = open(csv_pathname, 'w')
            quotechar = '"'        # default
        #    quotechar='|'
            csv_writer = csv.writer(csv_file,
                                    delimiter='\t',
                                    quoting=csv.QUOTE_NONNUMERIC,
                                    quotechar=quotechar)
        except Exception as e:
            msg = "opening CSV file failed: %s" % str(e)
            if settings.DEBUG:
                print >> stderr, msg
            resp_dict = {"status": "error", "msg": msg}
            json_list = json.dumps(resp_dict)
            ctype = 'application/json; charset=UTF-8'
            return HttpResponse(json_list, content_type=ctype)

    for ichunk in range(nchunks):
        start_record = ichunk * chunk_size
        nchunk = ichunk + 1

        if settings.DEBUG:
            print >> stderr, "nchunk:", nchunk, "of", nchunks, \
                             "start_record:", start_record

        hits, resp_obj = get_es_chunk(params, start_record, chunk_size)

        hits_list = hits["hits"]
        hits_zipped += len(hits_list)
        zip_chunk(ichunk, hits_list, zip_file, csv_writer, format)

    if format == "csv":
        csv_file.close()
        csv_file = open(csv_pathname, 'r')
        zip_file.writestr(csv_filename, csv_file.read())
        csv_file.close()
        if settings.DEBUG:
            print >> stderr, "deleting %s" % csv_pathname
        os.remove(csv_pathname)     # not needed anymore

    if settings.DEBUG:
        print >> stderr, "hits_zipped:", hits_zipped

    # send email
    from_email = "j.vanderzwaan@esciencecenter.nl"
    to_email = to_email
    subject = "Texcavator data download"
    msg = "sending email to %s" % to_email
    logger.debug(msg)
    if settings.DEBUG:
        print >> stderr, msg
    send_mail(subject,
              email_message,
              from_email,
              [to_email],
              fail_silently=False)


def zip_chunk(ichunk, hits_list, zip_file, csv_writer, format):
    msg = "%s: %s" % (__name__, "zip_chunk()")
    logger.debug(msg)
    if settings.DEBUG:
        print >> stderr, msg

    if hits_list is None:
        print >> stderr, "zip_chunk(): empty hit list"
        return

    for h in range(len(hits_list)):
        hit = hits_list[h]

        _id = hit["_id"]

        # use '-' instead of ':' in file names
        pseudo_filename = _id.replace(':', '-')
        if format == "xml":
            pseudo_filename += ".xml"
            xml = dicttoxml(hit)
            zip_file.writestr(pseudo_filename, xml.encode("utf-8"))
        elif format == "csv":
            if h == 0:
                es_header_names, kb_header_names = hit2csv_header(csv_writer,
                                                                  ichunk,
                                                                  hit)
            hit2csv_data(csv_writer, hit, es_header_names, kb_header_names)
        else:         # "json"
            pseudo_filename += ".json"
            zip_file.writestr(pseudo_filename, json.dumps(hit))


def hit2csv_header(csv_writer, ichunk, hit):
    es_header_names = ["_id", "_score"]

    kb_header_names = \
        ["identifier",                        # 2

         "paper_dc_date",                    # 3
         "paper_dc_identifier",                # 4
         "paper_dc_identifier_resolver",        # 5
         "paper_dc_language",                # 6
         "paper_dc_title",                    # 7
         "paper_dc_publisher",                # 8
         "paper_dc_source",                    # 9

         "paper_dcterms_alternative",         # 10
         "paper_dcterms_isPartOf",            # 11
         "paper_dcterms_isVersionOf",        # 12
         "paper_dcterms_issued",                # 13
         "paper_dcterms_spatial",            # 14
         "paper_dcterms_spatial_creation",     # 15
         "paper_dcterms_temporal",            # 16

         "paper_dcx_issuenumber",   # 17 can contain '-' instead of a number
         "paper_dcx_recordRights",              # 18
         "paper_dcx_recordIdentifier",         # 19
         "paper_dcx_volume",                    # 20

         "paper_ddd_yearsDigitized",            # 21

         "article_dc_identifier_resolver",    # 21
         "article_dc_subject",                # 22
         "article_dc_title",                    # 23
         "article_dcterms_accessRights",        # 24
         "article_dcx_recordIdentifier",        # 25

         "text_content"]                        # 26

    header_names = es_header_names + kb_header_names

    if ichunk == 0:
        csv_writer.writerow(header_names)

    return es_header_names, kb_header_names


def hit2csv_data(csv_writer, hit, es_header_names, kb_header_names):
    es_line = []
    for es_name in es_header_names:
        try:
            val = hit[es_name]
        except:
            val = ""
        es_line.append(val)

    kb_line = []
    _source = hit["_source"]
    for kb_name in kb_header_names:
        try:
            # in number fields, this troubles Jose's SPSS
            if _source[kb_name] == '-':
                val = ''
            else:
                val = _source[kb_name].replace('\n', ' ').encode("utf-8")
        except:
            val = ""
        kb_line.append(val)

    data_line = es_line + kb_line

    csv_writer.writerow(data_line)


def get_es_chunk(params, start_record, chunk_size):
    """Retrieve a # chunksize documents from ElasticSearch index."""
    msg = "%s: %s" % (__name__, "get_es_chunk")
    logger.debug(msg)
    if settings.DEBUG:
        print >> stderr, msg

    validity, es_dict = do_search(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  params['query'],
                                  start_record,
                                  chunk_size,
                                  params['dates'],
                                  params['distributions'],
                                  params['article_types'],
                                  True)

    return es_dict['hits'], None


def clean_filename(s):
    # strip problematic characters from filename
    s = ''.join((c for c in unicodedata.normalize('NFD', s)
                 if unicodedata.category(c) != 'Mn'))
    s = s.replace(' ', '_')
    s = "".join(i for i in s if (i.isalnum() or i == '_'))
    return s


def execute(merge_dict, zip_basename, to_email, email_message):
    if settings.DEBUG:
        print >> stderr, "execute()"
    logger.debug("%s: %s" % (__name__, "execute()"))

    if settings.QUERY_DATA_DELETE_DATA:
        expire_data()        # delete old download stuff

    keys = merge_dict.keys()
    values = merge_dict.values()
    req_dict = {}
    for i in range(len(keys)):
        req_dict[keys[i]] = values[i]

    # add the zip name & user email
    req_dict["zip_basename"] = zip_basename
    req_dict["to_email"] = to_email
    req_dict["email_message"] = email_message
    if settings.DEBUG:
        print >> stderr, req_dict
        print type(req_dict)

    req_str = json.dumps(req_dict)
    req_base64 = base64.b64encode(req_str)
    if settings.DEBUG:
        print >> stderr, req_base64

    vpython = settings.QUERY_DATA_VPYTHON_PATH + "/bin/activate"
    program = os.path.join(settings.PROJECT_PARENT, "manage.py")

    if settings.QUERY_DATA_DOWNLOAD_DETACH:
        # need to set proper environment
        cmdline = "source " + vpython + "; "
        cmdline += 'python ' + program + ' zipquerydata "' + req_base64 + '"'
        if settings.DEBUG:
            print cmdline, "\n"

        p = subprocess.Popen(cmdline, shell=True, close_fds=True)
        resp_str = ""
    else:    # this cmd waits until completion, defaul: close_fds=False
        cmdline += 'python ' + program + ' zipquerydata "' + req_base64 + '"'
        if settings.DEBUG:
            print cmdline, "\n"

        p = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE)
        resp_str = p.stdout.read()
        if settings.DEBUG:
            print >> stderr, "resp_str: |%s|" % resp_str

    return resp_str


def expire_data():
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
                msg = "deleting qyery data file failed: %s" % str(e)
                logger.debug(msg)
                if settings.DEBUG:
                    print >> stderr, msg

        else:
            msg = "keeping query data file: %s" % fpath
            logger.debug(msg)
            if settings.DEBUG:
                print>> stderr, msg
