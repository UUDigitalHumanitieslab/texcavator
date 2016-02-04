# -*- coding: utf-8 -*-
"""Elasticsearch functionality"""

import json
import logging
import os
from collections import Counter, defaultdict
from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch.client import indices

from django.conf import settings

from texcavator.utils import daterange2dates

logger = logging.getLogger(__name__)

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

_DOCUMENT_TEXT_FIELD = 'text_content'
_DOCUMENT_TITLE_FIELD = 'article_dc_title'
_AGG_FIELD = _DOCUMENT_TEXT_FIELD
_STEMMING_ANALYZER = 'dutch_analyzer'


def _es():
    """Returns ElasticSearch instance."""
    node = {'host': settings.ELASTICSEARCH_HOST,
            'port': settings.ELASTICSEARCH_PORT}
    if settings.ELASTICSEARCH_USERNAME:
        node['http_auth'] = (settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD)
        node['use_ssl'] = settings.ELASTICSEARCH_USE_SSL
    return Elasticsearch([node])


def do_search(idx, typ, query, start, num, date_ranges, exclude_distributions,
              exclude_article_types, selected_pillars, return_source=False, sort_order='_score'):
    """Returns ElasticSearch search results.

    Fetch all documents matching the query and return a list of
    elasticsearch results.

    This method accepts boolean queries in the Elasticsearch query string
    syntax (see Elasticsearch reference).

    Parameters:
        idx : str
            The name of the elasticsearch index
        typ : str
            The type of document requested
        query : str
            A query string in the Elasticsearch query string language
        start : int
            An integer representing the index of the first result to be
            retrieved
        num : int
            The total number of results to be retrieved
        date_ranges : list(dict)
            A list of dictionaries containg the upper and lower dates of the
            requested date ranges
        exclude_distributions : list
            A list of strings respresenting distributions that should be
            excluded from the search
        exclude_article_types : list
            A list of strings representing article types that should be
            excluded from the search
        selected_pillars : list
            A list of string representing pillars that should be included into
            the search. Each pillar is linked to a list of newspapers.
        return_source : boolean, optional
            A boolean indicating whether the _source of ES documents should be
            returned or a smaller selection of document fields. The smaller set
            of document fields (stored in _ES_RETURN_FIELDS) is the default
        sort_order: string, optional
            The sort order for this query. Syntax is fieldname:order, multiple
            sort orders can be separated by commas. Note that if the sort_order
            doesn't contain _score, no scores will be returned.

    Returns:
        validity : boolean
            A boolean indicating whether the input query string is valid.
        results : list
            A list of elasticsearch results or a message explaining why the
            input query string is invalid.
    """
    q = create_query(query, date_ranges, exclude_distributions,
                     exclude_article_types, selected_pillars)

    valid_q = indices.IndicesClient(_es()).validate_query(index=idx,
                                                          doc_type=typ,
                                                          body=q,
                                                          explain=True)

    if valid_q.get('valid'):
        if return_source:
            # for each document return the _source field that contains all
            # document fields (no fields parameter in the ES call)
            return True, _es().search(index=idx, doc_type=typ, body=q,
                                      from_=start, size=num, sort=sort_order)
        else:
            # for each document return the fields listed in_ES_RETURN_FIELDS
            return True, _es().search(index=idx, doc_type=typ, body=q,
                                      fields=_ES_RETURN_FIELDS, from_=start,
                                      size=num, sort=sort_order)
    return False, valid_q.get('explanations')[0].get('error')


def count_search_results(idx, typ, query, date_range, exclude_distributions,
                         exclude_article_types, selected_pillars):
    """Count the number of results for a query
    """
    q = create_query(query, date_range, exclude_distributions,
                     exclude_article_types, selected_pillars)

    return _es().count(index=idx, doc_type=typ, body=q)


def get_document(idx, typ, doc_id):
    """Return a document given its id.

    Parameters:
        idx : str
            The name of the elasticsearch index
        typ : str
            The type of document requested
        doc_id : str
            The id of the document to be retrieved
    """
    try:
        result = _es().get(index=idx, doc_type=typ, id=doc_id)
    except:
        return None

    return result['_source']


def create_query(query_str, date_ranges, exclude_distributions,
                 exclude_article_types, selected_pillars):
    """Create elasticsearch query from input string.

    This method accepts boolean queries in the Elasticsearch query string
    syntax (see Elasticsearch reference).

    Returns a dict that represents the query in the elasticsearch query DSL.
    """

    filter_must = []
    filter_should = []
    filter_must_not = []

    for date_range in date_ranges:
        filter_should.append(
            {
                'range': {
                    'paper_dc_date': {
                        'gte': date_range['lower'],
                        'lte': date_range['upper']
                    }
                }
            }
        )

    # Filters on newspapers. This reads from a local file; as Celery can't read from the database.
    newspaper_ids = []
    if selected_pillars:
        try:
            with open(os.path.join(settings.PROJECT_PARENT, 'newspapers.txt'), 'rb') as in_file:
                categorization = json.load(in_file)
                for pillar, n_ids in categorization.iteritems():
                    if int(pillar) in selected_pillars:
                        newspaper_ids.extend(n_ids)
        except IOError:
            logging.warning('No newspaper classification found. Continuing without filter on newspapers.')
    if newspaper_ids:
        filter_must.append({'terms': {'paper_dc_identifier': newspaper_ids}})

    for ds in exclude_distributions:
        filter_must_not.append(
            {"term": {"paper_dcterms_spatial": _KB_DISTRIBUTION_VALUES[ds]}})

    for typ in exclude_article_types:
        filter_must_not.append(
            {"term": {"article_dc_subject": _KB_ARTICLE_TYPE_VALUES[typ]}})

    query = {
        'query': {
            'filtered': {
                'filter': {
                    'bool': {
                        'must': filter_must,
                        'should': filter_should,
                        'must_not': filter_must_not
                    }
                }
            }
        }
    }

    # Add the query string part.
    if query_str:
        # Temporary hotfix for duplicate newspapers, see #73.
        if getattr(settings, 'KB_HOTFIX_DUPLICATE_NEWSPAPERS', True):
            query_str += ' -identifier:ddd\:11*'
        alw = getattr(settings, 'QUERY_ALLOW_LEADING_WILDCARD', True)
        query['query']['filtered']['query'] = {'query_string': {'query': query_str, 'allow_leading_wildcard': alw}}

    return query


def create_ids_query(ids):
    """Returns an Elasticsearch ids query.

    Create Elasticsearch query that returns documents based on a list of
    ids.

    Parameters:
        ids : list
            A list containing document ids

    Returns:
        query : dict
            A dictionary representing an ES ids query
    """
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
    """Create ES query to gather day statistics for the given date range.

    This function is used by the gatherstatistics management command.
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
    """Return aggragation part of terms aggregation (=word cloud) that can be
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


def single_document_word_cloud(idx, typ, doc_id, min_length=0, stopwords=[], stems=False):
    """Return data required to draw a word cloud for a single document.

    Parameters:
        idx : str
            The name of the elasticsearch index
        typ : str
            The type of document requested
        doc_id : str
            The id of the document the word cloud should be created for
        min_length : int, optional
            The minimum length of words in the word cloud
        stopwords : list, optional
            A list of words that should be removed from the word cloud
        stems : boolean, optional
            Whether or not we should look at the stemmed columns

    Returns:
        dict : dict
            A dictionary that contains word frequencies for all the terms in
            the document.

            .. code-block:: javascript

                {
                    'status': 'ok',
                    'result':
                        {
                            term: count
                        },
                        ...
                }
    """

    if not doc_id:
        return {
            'status': 'error',
            'error': 'No document id provided.'
        }

    bdy = {
        'fields': get_cloud_fields(stems)
    }
    t_vector = _es().termvector(index=idx, doc_type=typ, id=doc_id, body=bdy)

    if t_vector.get('found', False):
        wordcloud = Counter()
        for field, data in t_vector.get('term_vectors').iteritems():
            for term, count_dict in data.get('terms').iteritems():
                if term not in stopwords and len(term) >= min_length:
                    wordcloud[term] += int(count_dict.get('term_freq'))

        return {
            'result': wordcloud,
            'status': 'ok'
        }

    return {
        'status': 'error',
        'error': 'Document with id "{}" could not be found.'.format(doc_id)
    }


def multiple_document_word_cloud(idx, typ, query, date_ranges, dist, art_types, pillars,
                                 ids=None):
    """Return data required to draw a word cloud for multiple documents

    This function generates word cloud data using terms aggregations in ES.
    However, for newspaper articles this approach is not feasible; ES runs out
    of memory very quickly. Therefore, another approach to generating word
    cloud data was added: termvector_word_cloud

    See also:
        :func:`single_document_word_cloud` generate data for a single document
        word cloud

        :func:`termvector_word_cloud` generate word cloud data using termvector
        approach
    """
    if not ids:
        ids = []

    agg_name = 'words'

    # word cloud based on query
    if query:
        q = create_query(query, date_ranges, dist, art_types, pillars)
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


def termvector_wordcloud(idx, typ, doc_ids, min_length=0, stems=False, add_freqs=True):
    """Return word frequencies in a set of documents.

    Return data required to draw a word cloud for multiple documents by
    'manually' merging termvectors.

    The counter returned by this method can be transformed into the input
    expected by the interface by passing it to the normalize_cloud
    method.

    Parameters:
        idx : str
            The name of the elasticsearch index
        typ : str
            The type of document requested
        doc_ids : list(str)
            The requested documents
        min_length : int, optional
            The minimum length of words in the word cloud
        stems : boolean, optional
            Whether or not we should look at the stemmed columns
        add_freqs : boolean, optional
            Whether or not we should count total occurrences

    See also
        :func:`single_document_word_cloud` generate data for a single document
        word cloud

        :func:`multiple_document_word_cloud` generate word cloud data using
        terms aggregation approach
    """
    wordcloud = Counter()

    # If no documents are provided, return an empty counter.
    if not doc_ids:
        return wordcloud

    bdy = {
        'ids': doc_ids,
        'parameters': {
            'fields': get_cloud_fields(stems),
            'term_statistics': False,
            'field_statistics': False,
            'offsets': False,
            'payloads': False,
            'positions': False
        }
    }

    t_vectors = _es().mtermvectors(index=idx, doc_type=typ, body=bdy)

    for doc in t_vectors.get('docs'):
        temp = defaultdict(int) if add_freqs else set()
        for field, data in doc.get('term_vectors').iteritems():
            for term, details in data.get('terms').iteritems():
                if len(term) >= min_length:
                    if add_freqs:
                        temp[term] += int(details['term_freq'])
                    else:
                        temp.add(term)  # only count individual occurrences
        wordcloud.update(temp)

    return wordcloud


def get_search_parameters(req_dict):
    """Return a tuple of search parameters extracted from a dictionary

    Parameters:
        req_dict : dict
            A Django request dictionary

    Returns:
        dict : dict
            A dictionary that contains query metadata
    """
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

    pillars = [int(x) for x in req_dict.getlist('pillars')]
    collection = req_dict.get('collection', settings.ES_INDEX)
    sort_order = req_dict.get('sort_order', '_score')

    return {
        'query': query_str,
        'start': start,
        'result_size': result_size,
        'dates': dates,
        'distributions': distributions,
        'article_types': article_types,
        'pillars': pillars,
        'collection': collection,
        'sort_order': sort_order
    }


def get_document_ids(idx, typ, query, date_ranges, exclude_distributions=[],
                     exclude_article_types=[], selected_pillars=[]):
    """Return a list of document ids and dates for a query
    """
    doc_ids = []

    q = create_query(query, date_ranges, exclude_distributions,
                     exclude_article_types, selected_pillars)

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

        start += num

        if len(results['hits']['hits']) < num:
            get_more_docs = False

    return doc_ids


def document_id_chunks(chunk_size, idx, typ, query, date_ranges, dist=[],
                       art_types=[], selected_pillars=[]):
    """Generator for retrieving document ids for all results of a query.

    Used by the generate_tv_cloud task.
    """
    q = create_query(query, date_ranges, dist, art_types, selected_pillars)

    get_more_docs = True
    start = 0
    fields = []

    while get_more_docs:
        results = _es().search(index=idx, doc_type=typ, body=q, from_=start,
                               fields=fields, size=chunk_size)
        yield [result['_id'] for result in results['hits']['hits']]

        start = start + chunk_size

        if len(results['hits']['hits']) < chunk_size:
            get_more_docs = False


def day_statistics(idx, typ, date_range, agg_name):
    """Gather day statistics for all dates in the date range

    This function is used by the gatherstatistics management command.
    """
    q = create_day_statistics_query(date_range, agg_name)

    results = _es().search(index=idx, doc_type=typ, body=q, size=0)

    if 'took' in results:
        return results
    return None


def metadata_aggregation(idx, typ, query, date_ranges,
                         exclude_distributions, exclude_article_types, selected_pillars):
    body = create_query(query, date_ranges,
                        exclude_distributions, exclude_article_types, selected_pillars)
    body['aggs'] = metadata_dict()
    return _es().search(index=idx, doc_type=typ, body=body, search_type='count')


def metadata_dict():
    return {
        "distribution": {
            "terms": {
                "field": "paper_dcterms_spatial"
            }
        },
        "articletype": {
            "terms": {
                "field": "article_dc_subject"
            }
        },
        "newspaper_ids": {
            "terms": {
                "field": "paper_dc_identifier"
            }
        },
        "newspapers": {
            "terms": {
                "field": "paper_dc_title.raw",
                "size": 10
            }
        }
    }


def get_cloud_fields(stems=False):
    """
    :param stems: Whether or not to use the stemmed versions of the fields.
    :return: The fields on which the word cloud has to be created
    """
    fields = [_DOCUMENT_TEXT_FIELD, _DOCUMENT_TITLE_FIELD]
    if stems and settings.STEMMING_AVAILABLE:
        fields = [f + '.stemmed' for f in fields]
    return fields


def get_stemmed_form(idx, word):
    """
    Returns the stemmed form of a word for this

    Parameters:
        idx : str
            The name of the elasticsearch index
        word : str
            The input word
    """
    result = indices.IndicesClient(_es()).analyze(index=idx, text=word, analyzer=_STEMMING_ANALYZER)
    return result['tokens'][0]['token']
