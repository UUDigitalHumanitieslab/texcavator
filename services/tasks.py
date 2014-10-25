# -*- coding: utf-8 -*-
"""Services celery tasks.
"""
from __future__ import absolute_import
from collections import Counter

from celery import shared_task

from django.conf import settings
from services.es import get_document_ids, termvector_wordcloud, \
    counter2wordclouddata
from texcavator import utils


@shared_task
def generate_tv_cloud(search_params, min_length, stopwords, ids=None):
    burst = True
    chunk_size = 1000
    wordcloud_counter = Counter()

    # get ids
    if not ids:
        burst = False
        doc_ids = get_document_ids(settings.ES_INDEX,
                                   settings.ES_DOCTYPE,
                                   search_params['query'],
                                   search_params['dates'],
                                   search_params['distributions'],
                                   search_params['article_types'])

        ids = [doc['identifier'] for doc in doc_ids]

    for subset in utils.chunks(ids, chunk_size):
        result = termvector_wordcloud(settings.ES_INDEX,
                                      settings.ES_DOCTYPE,
                                      subset,
                                      min_length)
        wordcloud_counter = wordcloud_counter + result

    return counter2wordclouddata(wordcloud_counter, burst, stopwords)
