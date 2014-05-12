# -*- coding: utf-8 -*-
"""Elasticsearch functionality"""

from datetime import date
from elasticsearch import Elasticsearch

from texcavator.settings import ELASTICSEARCH_HOST, ELASTICSEARCH_PORT

def _es():
    return Elasticsearch(ELASTICSEARCH_HOST + ":" + str(ELASTICSEARCH_PORT))

_ES_RETURN_FIELDS = ('article_dc_title', 
                     'paper_dcterms_temporal', 
                     'paper_dcterms_spatial', 
                     'paper_dc_title', 
                     'paper_dc_date')

_KB_DISTRIBUTION_VALUES = {'sd_national': 'Landelijk',
                           'sd_regional': 'Regionaal/lokaal',
                           'sd_antilles': 'Nederlandse Antillen',
                           'sd_surinam': 'Suriname',
                           'sd_indonesia': 'Nederlands-Indië / Indonesië' }

_KB_ARTICLE_TYPE_VALUES = {'st_article': 'artikel',
				           'st_advert': 'advertentie',
				           'st_illust': 'illustratie met onderschrift',
                           'st_family': 'familiebericht'}

def do_search(idx, typ, query, start, num, date_range, dist, art_types):
    """Fetch all documents matching the query and return a list of elasticsearch
    results.

    Parameters
    ----------
    idx : name of the elasticsearch index
    typ : the type of document requested
    query : a query string
        At the moment, the literal query string is inserted in the elasticsearch
        query. Functionality to handle more complex queries needs to be added.
    start : integer representing the index of the first result to be retrieved
    num : the total number of results to be retrieved
    date_range : a dictionary containg the upper and lower dates of the 
        requested date dateRange
    dist : list of distribution strings respresenting distribution that should 
        be excluded from search (the values in the list only contain keys of the 
        _KB_DISTRIBUTION_VALUES dict).
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

def create_query(query_str, date_range, dist, art_types):
    """Create elasticsearch query from input string.
    
    Returns a dict that represents the query in the elasticsearch query DSL.

    At the moment, the literal query string is inserted in the elasticsearch 
    query. Functionality to handle more complex queries needs to be added, as
    well as updating the date filter with the appropriate date range.

    Returns dict with ES DSL results
    """

    filter_must_not = []
    for ds in dist:
        filter_must_not.append(
            {"term": {"paper_dcterms_spatial": _KB_DISTRIBUTION_VALUES[ds]}} )

    
    for typ in art_types:
        filter_must_not.append(
            {"term": { "article_dc_subject": _KB_ARTICLE_TYPE_VALUES[typ] }})
        
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

