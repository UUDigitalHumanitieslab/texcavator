# -*- coding: utf-8 -*-
"""Task for creating a zipfile of a set of documents (query export).
Could in the future be implemented with Celery."""
import base64
import os
import logging
import json
import csv
import zipfile

from math import ceil
from time import time, localtime, strftime
from sys import exc_info, stderr
from dicttoxml import dicttoxml

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse

from services.es import do_search

logger = logging.getLogger(__name__)


def zipquerydata(*args):
    t1 = time()

    logger.debug(__name__)

    logger.debug("\n%s\n" % __name__)
    logger.debug("%d args\n" % len(args))
    for arg in args:
        logger.debug("arg: %s\n" % arg)

    if len(args) == 0:
        print "no parameters specified\n"
        return
    elif len(args) > 2:
        print "too many parameters specified\n"
        return
    else:
        arg_base64 = args[0]
        arg_str = base64.b64decode(arg_base64)
        print "arg_str: %s\n" % type(arg_str)
        logger.debug("arg_str: %s\n" % arg_str)

        arg_dict = json.loads(arg_str)
        logger.debug("arg_dict: %s\n" % type(arg_dict))
        logger.debug("arg_dict: %s\n" % arg_dict)

        create_zip(arg_dict)

    t2 = time()            # seconds since the epoch
    sec = (t2-t1)
    str_elapsed_sec = str(round(sec, 2)) + " sec"
    str_elapsed_min = str(round(sec/60.0, 2)) + " min"

    logger.debug("finished in %s = %s\n"
                 % (str_elapsed_sec, str_elapsed_min))


def create_zip(req_dict):
    zip_basedir = os.path.join(settings.PROJECT_PARENT,
                               settings.QUERY_DATA_DOWNLOAD_PATH)
    zip_basename = req_dict["zip_basename"]

    fname_debug = zip_basename + ".txt"
    fpath_debug = os.path.join(zip_basedir, fname_debug)
    logger.debug("%s\n" % fpath_debug)

    # Create the directory if it doesn't exist
    if not os.path.exists(zip_basedir):
        os.makedirs(zip_basedir)

    try:
        file_debug = open(fpath_debug, 'w')
    except:
        type, value, tb = exc_info()
        msg = "creating %s failed\n" % fname_debug
        logger.debug(msg)
        if settings.DEBUG:
            logger.debug(msg)
        return

    try:
        now = strftime("%Y-%m-%d %H:%M:%S", localtime())
        logger.debug("start: %s\n" % now)
        file_debug.write("start: %s\n" % now)
        file_debug.write("%s\n" % __name__)
    except:
        logger.debug("writing %s failed\n" % fname_debug)

    logger.debug("create_zip()")
    logger.debug("req_dict: %s\n" % req_dict)

    zip_basename = req_dict["zip_basename"]
    req_dict.pop("zip_basename")
    logger.debug("zip_basename: %s\n" % zip_basename)

    to_email = req_dict["to_email"]
    req_dict.pop("to_email")
    logger.debug("to_email: %s\n" % to_email)

    email_message = req_dict["email_message"]
    req_dict.pop("email_message")
    logger.debug("email_message: %s\n" % email_message)

    msg = "calling download_collect..."
    logger.debug("%s\n" % msg)
    file_debug.write("%s\n" % msg)
    logger.debug(msg)

    file_debug.flush()
    download_collect(req_dict, zip_basename, to_email, email_message)

    msg = "returned from download_collect"
    logger.debug("%s\n" % msg)
    file_debug.write("%s\n" % msg)
    logger.debug(msg)

    try:
        now = strftime("%Y-%m-%d %H:%M:%S", localtime())
        logger.debug("end: %s\n" % now)
        file_debug.write("end: %s\n" % now)
    except:
        logger.debug("writing %s failed\n" % fname_debug)

    file_debug.close()


def download_collect(req_dict, zip_basename, to_email, email_message):
    """ Collect the documents and put them in a zipfile.
    """
    msg = "%s: %s" % (__name__, "download_collect()")
    logger.debug(msg)
    if settings.DEBUG:
        print >> stderr, msg

    # download format: JSON or XML
    format = req_dict.get('format', 'json')
    if settings.DEBUG:
        print >> stderr, "format", format

    msg = "es_query: %s" % req_dict['query']
    logger.debug(msg)

    # just get the hit count
    start_record = 0
    chunk_1_size = 1
    hits, resp_object = get_es_chunk(req_dict, start_record, chunk_1_size)

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

        hits, resp_obj = get_es_chunk(req_dict, start_record, chunk_size)

        hits_list = hits["hits"]
        hits_zipped += len(hits_list)
        zip_chunk(req_dict, ichunk, hits_list, zip_file, csv_writer, format)

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
    from_email = 'digitalhumanities@uu.nl'
    to_email = to_email
    subject = 'Texcavator data download'
    msg = 'sending email to %s' % to_email
    logger.debug(msg)
    if settings.DEBUG:
        print >> stderr, msg
    send_mail(subject,
              email_message,
              from_email,
              [to_email],
              fail_silently=False)


def get_es_chunk(req_dict, start_record, chunk_size):
    """Retrieve a # chunksize documents from ElasticSearch index."""
    msg = "%s: %s" % (__name__, "get_es_chunk")
    logger.debug(msg)
    if settings.DEBUG:
        print >> stderr, msg

    validity, es_dict = do_search(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  req_dict['query'],
                                  start_record,
                                  chunk_size,
                                  req_dict['dates'],
                                  req_dict['exclude_distributions'],
                                  req_dict['exclude_article_types'],
                                  True)

    return es_dict['hits'], None


def zip_chunk(req_dict, ichunk, hits_list, zip_file, csv_writer, format):
    """Zip a chunk of documents.

    Documents are retrieved from elasticsearch in chunks.
    """
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
                if ichunk == 0:
                    hit2csv_metadata(csv_writer, req_dict)
                es_header_names, kb_header_names = hit2csv_header(csv_writer, ichunk)
            hit2csv_data(csv_writer, hit, es_header_names, kb_header_names)
        else:         # "json"
            pseudo_filename += ".json"
            zip_file.writestr(pseudo_filename, json.dumps(hit))


def hit2csv_metadata(csv_writer, req_dict):
    """Writes the metadata rows
    """
    md_header = ['comment',
                 'query',
                 'date executed',
                 'excluded article types',
                 'excluded distributions',
                 'date lower',
                 'date upper']
    md_row = [req_dict['comment'],
              req_dict['query'],
              req_dict['date_created'],
              req_dict['exclude_article_types'],
              req_dict['exclude_distributions'],
              req_dict['date_lower'],
              req_dict['date_upper']]
    csv_writer.writerow(md_header)
    csv_writer.writerow(md_row)


def hit2csv_header(csv_writer, ichunk):
    """Returns the header row of the csv that is created.
    """
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
    """Writes a single document to the csv file.
    """
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
