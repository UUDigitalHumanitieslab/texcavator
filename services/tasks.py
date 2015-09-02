# -*- coding: utf-8 -*-
"""Services celery tasks.
"""
from __future__ import absolute_import

from collections import Counter

from celery import shared_task, current_task

from django.conf import settings

from services.es import document_id_chunks, termvector_wordcloud, \
    counter2wordclouddata, count_search_results


@shared_task
def generate_tv_cloud(search_params, min_length, stopwords, date_range=None, stems=False):
    """Generates multiple document word clouds using the termvector approach"""
    chunk_size = settings.QUERY_DATA_CHUNK_SIZE
    progress = 0
    wordcloud_counter = Counter()

    # Date range is either provided or from the Query
    dates = date_range or search_params['dates']

    # First, count the search results
    result = count_search_results(settings.ES_INDEX,
                                  settings.ES_DOCTYPE,
                                  search_params['query'],
                                  dates,
                                  search_params['exclude_distributions'],
                                  search_params['exclude_article_types'],
                                  search_params['selected_pillars'])
    doc_count = result.get('count')

    info = {
        'current': 0,
        'total': doc_count
    }
    current_task.update_state(state='PROGRESS', meta=info)

    # Then, create the word clouds per chunk
    for subset in document_id_chunks(chunk_size,
                                     settings.ES_INDEX,
                                     settings.ES_DOCTYPE,
                                     search_params['query'],
                                     dates,
                                     search_params['exclude_distributions'],
                                     search_params['exclude_article_types'],
                                     search_params['selected_pillars']):

        result = termvector_wordcloud(settings.ES_INDEX,
                                      settings.ES_DOCTYPE,
                                      subset,
                                      min_length,
                                      stems)
        wordcloud_counter = wordcloud_counter + result

        progress += len(subset)
        info = {
            'current': progress,
            'total': doc_count
        }
        current_task.update_state(state='PROGRESS', meta=info)

    burst = date_range is not None
    return counter2wordclouddata(wordcloud_counter, burst, stopwords)
