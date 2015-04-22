#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Management command for creating a zipfile of a set of documents (query
export).
"""
import base64
import os
from time import time, localtime, strftime
from sys import exc_info

import logging

import json

from django.conf import settings
from django.core.management.base import BaseCommand

from query.download import download_collect

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        t1 = time()

        logger.debug(__name__)

        self.stdout.write("\n%s\n" % __name__)
        self.stdout.write("%d args\n" % len(args))
        for arg in args:
            self.stdout.write("arg: %s\n" % arg)

        if len(args) == 0:
            self.stdout.write("no parameters specified\n")
            return
        elif len(args) > 2:
            self.stdout.write("too many parameters specified\n")
            return
        else:
            arg_base64 = args[0]
            arg_str = base64.b64decode(arg_base64)
            self.stdout.write("arg_str: %s\n" % type(arg_str))
            self.stdout.write("arg_str: %s\n" % arg_str)

            arg_dict = json.loads(arg_str)
            self.stdout.write("arg_dict: %s\n" % type(arg_dict))
            self.stdout.write("arg_dict: %s\n" % arg_dict)

            self.create_zip(arg_dict)

        t2 = time()            # seconds since the epoch
        sec = (t2-t1)
        str_elapsed_sec = str(round(sec, 2)) + " sec"
        str_elapsed_min = str(round(sec/60.0, 2)) + " min"

        self.stdout.write("finished in %s = %s\n"
                          % (str_elapsed_sec, str_elapsed_min))

    def create_zip(self, req_dict):
        zip_basedir = os.path.join(settings.PROJECT_PARENT,
                                   settings.QUERY_DATA_DOWNLOAD_PATH)
        zip_basename = req_dict["zip_basename"]

        fname_debug = zip_basename + ".txt"
        fpath_debug = os.path.join(zip_basedir, fname_debug)
        self.stdout.write("%s\n" % fpath_debug)

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
                self.stdout.write(msg)
            return

        try:
            now = strftime("%Y-%m-%d %H:%M:%S", localtime())
            self.stdout.write("start: %s\n" % now)
            file_debug.write("start: %s\n" % now)
            file_debug.write("%s\n" % __name__)
        except:
            self.stdout.write("writing %s failed\n" % fname_debug)

        self.stdout.write("create_zip()")
        self.stdout.write("req_dict: %s\n" % req_dict)

        zip_basename = req_dict["zip_basename"]
        req_dict.pop("zip_basename")
        self.stdout.write("zip_basename: %s\n" % zip_basename)

        to_email = req_dict["to_email"]
        req_dict.pop("to_email")
        self.stdout.write("to_email: %s\n" % to_email)

        email_message = req_dict["email_message"]
        req_dict.pop("email_message")
        self.stdout.write("email_message: %s\n" % email_message)

        msg = "calling download_collect..."
        self.stdout.write("%s\n" % msg)
        file_debug.write("%s\n" % msg)
        logger.debug(msg)

        file_debug.flush()
        download_collect(req_dict, zip_basename, to_email, email_message)

        msg = "returned from download_collect"
        self.stdout.write("%s\n" % msg)
        file_debug.write("%s\n" % msg)
        logger.debug(msg)

        try:
            now = strftime("%Y-%m-%d %H:%M:%S", localtime())
            self.stdout.write("end: %s\n" % now)
            file_debug.write("end: %s\n" % now)
        except:
            self.stdout.write("writing %s failed\n" % fname_debug)

        file_debug.close()
