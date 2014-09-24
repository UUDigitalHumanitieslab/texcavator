from __future__ import absolute_import

from celery import shared_task

from django.conf import settings
from services.es import get_document_ids, termvector_word_cloud


@shared_task
def generate_tv_cloud(search_params, min_length, stopwords):
    # get ids
    doc_ids = get_document_ids(settings.ES_INDEX,
                               settings.ES_DOCTYPE,
                               search_params['query'],
                               search_params['dates'],
                               search_params['distributions'],
                               search_params['article_types'])

    ids = [doc['identifier'] for doc in doc_ids]

    result = termvector_word_cloud(settings.ES_INDEX,
                                   settings.ES_DOCTYPE,
                                   ids,
                                   min_length,
                                   stopwords)
    return result
