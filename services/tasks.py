# -*- coding: utf-8 -*-
"""Services celery tasks.
"""
from __future__ import absolute_import

from collections import Counter

from celery import shared_task, current_task

from django.conf import settings

from services.es import document_id_chunks, termvector_wordcloud, \
    counter2wordclouddata, count_search_results
from texcavator import utils


@shared_task
def generate_tv_cloud(search_params, min_length, stopwords, ids=None):
    """Generates multiple document word clouds using the termvector approach"""
    burst = True
    chunk_size = 1000
    progress = 0
    wordcloud_counter = Counter()

    if not ids:
        # Normal (non-time line) wordcloud (based on query)
        burst = False

        result = count_search_results(settings.ES_INDEX,
                                      settings.ES_DOCTYPE,
                                      search_params['query'],
                                      search_params['dates'],
                                      search_params['distributions'],
                                      search_params['article_types'],
                                      search_params['pillars'])
        doc_count = result.get('count')

        info = {
            'current': 0,
            'total': doc_count
        }
        current_task.update_state(state='PROGRESS', meta=info)

        for subset in document_id_chunks(chunk_size,
                                         settings.ES_INDEX,
                                         settings.ES_DOCTYPE,
                                         search_params['query'],
                                         search_params['dates'],
                                         search_params['distributions'],
                                         search_params['article_types'],
                                         search_params['pillars']):

            result = termvector_wordcloud(settings.ES_INDEX,
                                          settings.ES_DOCTYPE,
                                          subset,
                                          min_length)
            wordcloud_counter = wordcloud_counter + result

            progress += len(subset)
            info = {
                'current': progress,
                'total': doc_count
            }
            current_task.update_state(state='PROGRESS', meta=info)
    else:
        # Time line word cloud (based in list of document ids)
        for subset in utils.chunks(ids, chunk_size):
            result = termvector_wordcloud(settings.ES_INDEX,
                                          settings.ES_DOCTYPE,
                                          subset,
                                          min_length)
            wordcloud_counter = wordcloud_counter + result

            progress += len(subset)
            info = {
                'current': progress,
                'total': len(ids)
            }
            current_task.update_state(state='PROGRESS', meta=info)

    return counter2wordclouddata(wordcloud_counter, burst, stopwords)
