from __future__ import absolute_import

import json
from celery import shared_task

from django.conf import settings
from texcavator.utils import json_response_message
from services.es import get_document_ids, termvector_word_cloud


@shared_task
def generate_tv_cloud(query, min_length, stopwords):
    dates = {'lower': query['date_lower'], 'upper': query['date_upper']}

    # get ids
    doc_ids = get_document_ids(settings.ES_INDEX,
                               settings.ES_DOCTYPE,
                               query['query'],
                               dates,
                               query['exclude_distributions'],
                               query['exclude_article_types'])

    ids = [doc['identifier'] for doc in doc_ids]

    result = termvector_word_cloud(settings.ES_INDEX,
                                   settings.ES_DOCTYPE,
                                   ids,
                                   min_length,
                                   stopwords)
    return result
