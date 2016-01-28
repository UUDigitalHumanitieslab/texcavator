# -*- coding: utf-8 -*-
"""Services celery tasks.
"""
from __future__ import absolute_import

import math
from itertools import dropwhile
from collections import Counter

from celery import shared_task, current_task

from django.conf import settings

from services.es import document_id_chunks, termvector_wordcloud, count_search_results
from texcavator.utils import normalize_cloud


@shared_task
def generate_tv_cloud(search_params, min_length, stopwords, date_range=None, stems=False, idf_timeframe=''):
    """
    Generates multiple document word clouds using the termvector approach.
    """
    # Date range is either provided (in case of burst clouds from the timelines) or from the Query
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
    update_task_status(0, doc_count)

    # Then, create the word clouds per chunk
    progress = 0
    wordcloud_counter = Counter()
    for subset in document_id_chunks(settings.QUERY_DATA_CHUNK_SIZE,
                                     settings.ES_INDEX,
                                     settings.ES_DOCTYPE,
                                     search_params['query'],
                                     dates,
                                     search_params['exclude_distributions'],
                                     search_params['exclude_article_types'],
                                     search_params['selected_pillars']):

        wordcloud_counter += termvector_wordcloud(settings.ES_INDEX,
                                                  settings.ES_DOCTYPE,
                                                  subset,
                                                  min_length,
                                                  stems)

        # Update the task status
        progress += len(subset)
        update_task_status(progress, doc_count)

    # Remove non-frequent words form the counter
    for key, count in dropwhile(lambda c: c[1] > math.log10(doc_count), wordcloud_counter.most_common()):
        del wordcloud_counter[key]

    # Remove the stopwords from the counter
    for sw in stopwords:
        del wordcloud_counter[sw]

    # Return a dictionary with the results
    return {
        'result': normalize_cloud(wordcloud_counter, idf_timeframe),
        'status': 'ok',
        'burstcloud': date_range is not None
    }


def update_task_status(progress, total):
    """
    Updates the current task with the progress
    """
    info = {
        'current': progress,
        'total': total
    }
    current_task.update_state(state='PROGRESS', meta=info)

