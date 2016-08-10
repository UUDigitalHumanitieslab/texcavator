# -*- coding: utf-8 -*-

""" Old ElasticSearch BiLand functionality.

This module must be removed.
"""

from sys import stderr

from django.conf import settings


def elasticsearch_htmlresp(start_record, chunk_size, es_dict):
    """Create HTML response from ElasticSearch request.

    Parameters:
        start_record : int
            Search results are returned as a numbered list. The start record is
            the number this list should start with (pagination).
        chunk_size : int
            The number of results displayed.
        es_dict : dictionary
            Dictionary returned by ElasticSearch for a search request (contains
            the returned documents).

    Returns:
        string : str
            The html string for displaying the search results.
    """
    if settings.DEBUG:
        print >> stderr, "elasticsearch_htmlresp()"

    hits = es_dict["hits"]
    hits_total = hits["total"]
    hits_max_score = hits["max_score"]
    hits_list = hits["hits"]
    hits_retrieved = len(hits_list)

    html_str = ''
    if hits_retrieved != hits_total:  # did not get everything
        html_str += paging_links(start_record, chunk_size, hits_total)
    if hits_total == 0 or not hits_max_score:
        html_str += '<p>Found ' + "%s" % hits_total + ' records.'
    else:
        html_str += '<p>Found ' + "%s" % hits_total + ' records, '
        html_str += 'max score = ' + "%1.2f" % hits_max_score + '.</p>'

    html_str += '<ol start="' + '%s' % start_record + '">'

    for h in range(hits_retrieved):
        hit = hits_list[h]

        _id = hit["_id"]
        _score = hit["_score"]

        article_dc_title = hit["fields"]["article_dc_title"][0]
        paper_dcterms_temporal = hit["fields"]["paper_dcterms_temporal"][0]
        paper_dcterms_spatial = hit["fields"]["paper_dcterms_spatial"][0]

        paper_dc_title = hit["fields"]["paper_dc_title"][0]
        paper_dc_date = hit["fields"]["paper_dc_date"][0]

        item_str = u'<li id="{}">'.format(_id)
        item_str += u'<a href="javascript:retrieveRecord(\'{}\');" title="{}">'.format(_id, article_dc_title)

        if len(article_dc_title) > 45:  # limit displayed title length
            item_str += '<b>' + article_dc_title[0:45] + '</b>...</a>'
        else:
            item_str += '<b>' + article_dc_title + '</b></a>'

        item_str += '<br>' + paper_dc_title
        item_str += '<br>' + paper_dc_date

        if paper_dcterms_temporal != "":
            item_str += ', ' + paper_dcterms_temporal
        if paper_dcterms_spatial != "":
            item_str += ', ' + paper_dcterms_spatial

        if _score:
            item_str += ' [score: '
            item_str += "%1.2f" % _score
            item_str += ']'

        item_str += "</li>"
        html_str += item_str

    html_str += '</ol>'
    html_str += paging_links(start_record, chunk_size, hits_total)
    html_str += '<a href="#search">Back to top</a>'

    return html_str


def paging_links(start_record, chunk_size, hits_total):
    have_prev = start_record > 1
    have_next = start_record + chunk_size < hits_total

    href_prev = '<a href="javascript:nextResults(-' + str(chunk_size) + ');">previous</a>'
    href_next = '<a href="javascript:nextResults(+' + str(chunk_size) + ');">next</a>'

    result = '<span style="float:right">'
    if have_prev and have_next:
        result += href_prev + ' | ' + href_next
    elif have_prev:
        result += href_prev
    elif have_next:
        result += href_next
    result += '</span>'

    return result
