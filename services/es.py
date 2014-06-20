# -*- coding: utf-8 -*-
"""Elasticsearch functionality"""


from django.conf import settings

import json
from datetime import datetime
from elasticsearch import Elasticsearch

_ES_RETURN_FIELDS = ('article_dc_title',
                     'paper_dcterms_temporal',
                     'paper_dcterms_spatial',
                     'paper_dc_title',
                     'paper_dc_date')

_KB_DISTRIBUTION_VALUES = {'sd_national': 'Landelijk',
                           'sd_regional': 'Regionaal/lokaal',
                           'sd_antilles': 'Nederlandse Antillen',
                           'sd_surinam': 'Suriname',
                           'sd_indonesia': 'Nederlands-Indië / Indonesië'}

_KB_ARTICLE_TYPE_VALUES = {'st_article': 'artikel',
                           'st_advert': 'advertentie',
                           'st_illust': 'illustratie met onderschrift',
                           'st_family': 'familiebericht'}

_DOCUMENT_TEXT_FIELD = 'text'
_AGG_FIELD = 'text'


def _es():
    return Elasticsearch(settings.ELASTICSEARCH_HOST + ":" +
                         str(settings.ELASTICSEARCH_PORT))


def do_search(idx, typ, query, start, num, date_range, dist, art_types):
    """Fetch all documents matching the query and return a list of
    elasticsearch results.

    Parameters
    ----------
    idx : name of the elasticsearch index
    typ : the type of document requested
    query : a query string
        At the moment, the literal query string is inserted in the
        elasticsearch query. Functionality to handle more complex queries needs
        to be added.
    start : integer representing the index of the first result to be retrieved
    num : the total number of results to be retrieved
    date_range : a dictionary containg the upper and lower dates of the
        requested date dateRange
    dist : list of distribution strings respresenting distribution that should
        be excluded from search (the values in the list only contain keys of
        the _KB_DISTRIBUTION_VALUES dict).
    art_types : list of article types (entry values are specified by the keys
        of the _KB_ARTICLE_TYPE_VALUES dict.

    Returns
    -------
    results : list
        A list of elasticsearch results.
    """
    q = create_query(query, date_range, dist, art_types)

    return _es().search(index=idx, doc_type=typ, body=q,
                        fields=_ES_RETURN_FIELDS, from_=start, size=num)


def count_search_results(idx, typ, query, date_range, dist, art_types):
    """Returns the result of an Elasticsearch count query
    """
    q = create_query(query, date_range, dist, art_types)

    return _es().count(index=idx, doc_type=typ, body=q)


def create_query(query_str, date_range, dist, art_types):
    """Create elasticsearch query from input string.

    Returns a dict that represents the query in the elasticsearch query DSL.

    At the moment, the literal query string is inserted in the elasticsearch
    query. Functionality to handle more complex queries needs to be added.

    Returns dict with an ES DSL query
    """

    filter_must_not = []
    for ds in dist:
        filter_must_not.append(
            {"term": {"paper_dcterms_spatial": _KB_DISTRIBUTION_VALUES[ds]}})

    for typ in art_types:
        filter_must_not.append(
            {"term": {"article_dc_subject": _KB_ARTICLE_TYPE_VALUES[typ]}})

    query = {
        'query': {
            'filtered': {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'match': {
                                    '_all': {
                                        'query': query_str
                                    }
                                }
                            }
                        ]
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'range': {
                                    'paper_dc_date': {
                                        'gte': date_range['lower'],
                                        'lte': date_range['upper']
                                    }
                                }
                            }
                        ],
                        'must_not': filter_must_not
                    }
                }
            }
        }
    }

    return query


def create_ids_query(ids):
    """Create Elasticsearch query that returns documents based on a list of
    ids."""
    query = {
        'query': {
            'filtered': {
                'filter': {
                    'ids': {
                        'type': settings.ES_DOCTYPE,
                        'values': ids
                    }
                }
            }
        }
    }

    return query


def create_day_statistics_query(date_range, agg_name):
    """Create elasticsearch aggregation query to gather day statistics for the
    given date range.
    """
    date_lower = datetime.strptime(date_range['lower'], '%Y-%m-%d').date()
    date_upper = datetime.strptime(date_range['upper'], '%Y-%m-%d').date()
    diff = date_upper-date_lower
    num_days = diff.days

    return {
        'query': {
            'filtered': {
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'range': {
                                    'paper_dc_date': {
                                        'gte': date_range['lower'],
                                        'lte': date_range['upper']
                                    }
                                }
                            }
                        ]
                    }
                },
                'query': {
                    'match_all': {}
                }
            }
        },
        'aggs': {
            agg_name: {
                'terms': {
                    'field': 'paper_dc_date',
                    'size': num_days
                }
            }
        },
        'size': 0
    }


def word_cloud_aggregation(agg_name, num_words=100):
    """Return aggragation part of terms (=word cloud) aggregation that can be
    added to any Elasticsearch query."""
    agg = {
        agg_name: {
            'terms': {
                'field': _AGG_FIELD,
                'size': num_words
            }
        }
    }

    return agg


def single_document_word_cloud(idx, typ, doc_id):
    """Return data required to draw a word cloud for a single document.

    Returns a dict that contains word frequencies for all the terms in the
    document. The data returned is formatted according to what is expected by
    the user interface:
    {
        'status': 'ok'
        'max_count': ...
        'result':
            [
                {
                    'term': ...
                    'count': ...
                },
                ...
            ]
    }
    """

    if not doc_id:
        return {
            'status': 'error',
            'error': 'No document id provided.'
        }

    bdy = {
        'fields': [_DOCUMENT_TEXT_FIELD]
    }
    t_vector = _es().termvector(index=idx, doc_type=typ, id=doc_id, body=bdy)

    if t_vector.get('found', False):
        result = []
        max_count = 0
        for term, count_dict in t_vector.get('term_vectors'). \
                get(_DOCUMENT_TEXT_FIELD).get('terms').iteritems():

            count = count_dict.get('term_freq')
            if count > max_count:
                max_count = count

            result.append(
                {
                    'term': term,
                    'count': count
                })

        return {
            'max_count': max_count,
            'result': result,
            'status': 'ok'
        }

    return {
        'status': 'error',
        'error': 'Document with id "%s" could not be found.' % doc_id
    }


def multiple_document_word_cloud(idx, typ, query, date_range, dist, art_types,
                                 ids=None):
    """Return data required to draw a word cloud for multiple documents (i.e.,
    the results of a search query.

    See single_document_word_cloud().
    """
    if not ids:
        ids = []

    agg_name = 'words'

    # word cloud based on query
    if query:
        q = create_query(query, date_range, dist, art_types)
        q['aggs'] = word_cloud_aggregation(agg_name)
    # word cloud based on document ids
    elif not query and len(ids) > 0:
        q = create_ids_query(ids)
        q['aggs'] = word_cloud_aggregation(agg_name)
    else:
        return {
            'status': 'error',
            'error': 'No valid query provided for word cloud generation.'
        }

    aggr = _es().search(index=idx, doc_type=typ, body=q, size=0)

    aggr_result_list = aggr.get('aggregations').get(agg_name).get('buckets')
    max_count = aggr_result_list[0].get('doc_count')

    result = []
    for term in aggr_result_list:
        result.append({
            'term': term.get('key'),
            'count': term.get('doc_count')
        })

    return {
        'max_count': max_count,
        'result': result,
        'status': 'ok',
        'took': aggr.get('took', 0)
    }


def get_search_parameters(req_dict):
    """Return a tuple of search parameters extracted from a dictionary"""
    query_str = req_dict.get('query', None)

    start = int(req_dict.get('startRecord', 1))

    result_size = int(req_dict.get('maximumRecords', 20))

    date_range_str = req_dict.get('dateRange', settings.TEXCAVATOR_DATE_RANGE)
    dates = daterange2dates(date_range_str)

    distributions = []
    for ds in _KB_DISTRIBUTION_VALUES.keys():
        use_ds = json.loads(req_dict.get(ds, "true"))
        if not use_ds:
            distributions.append(ds)

    article_types = []
    for typ in _KB_ARTICLE_TYPE_VALUES:
        use_type = json.loads(req_dict.get(typ, "true"))
        if not use_type:
            article_types.append(typ)

    collection = req_dict.get('collection', settings.ES_INDEX)

    return {
        'query': query_str,
        'start': start,
        'result_size': result_size,
        'dates': dates,
        'distributions': distributions,
        'article_types': article_types,
        'collection': collection
        }


def daterange2dates(date_range_str):
    """Return a dictionary containing the date boundaries specified.

    If the input string does not specify two dates, the maximum date range is
    retrieved from the settings.
    """
    dates_str = date_range_str.split(',')
    if not len(dates_str) == 2:
        return daterange2dates(settings.TEXCAVATOR_DATE_RANGE)

    dates = [str(datetime.strptime(date, '%Y%m%d').date())
             for date in dates_str]
    return {'lower': min(dates), 'upper': max(dates)}


def get_document_ids(idx, typ, query, date_range, dist=[], art_types=[]):
    doc_ids = []

    q = create_query(query, date_range, dist, art_types)

    date_field = 'paper_dc_date'
    fields = [date_field]
    get_more_docs = True
    start = 0
    num = 2500

    while get_more_docs:
        results = _es().search(index=idx, doc_type=typ, body=q, fields=fields,
                               from_=start, size=num)
        for result in results['hits']['hits']:
            doc_ids.append(
                {
                    'identifier': result['_id'],
                    'date': datetime.strptime(result['fields'][date_field][0],
                                              '%Y-%m-%d').date()
                })

        start = start + num

        if len(results['hits']['hits']) < num:
            get_more_docs = False

    return doc_ids


def day_statistics(idx, typ, date_range, agg_name):
    q = create_day_statistics_query(date_range, agg_name)

    results = _es().search(index=idx, doc_type=typ, body=q, size=0)

    if 'took' in results:
        return results
    return None
