# -*- coding: utf-8 -*-
"""Models used for measuring ElasticSearch performance in management commands.
"""

from django.db import models


class DocID(models.Model):
    """Model for a document id used to generate queries of certain sizes

    This model is used to store document ids. The document ids are used to
    generate query sets of certain sizes. These query sets are used to test the
    performance of generating word cloud data using ES in multiple management
    commands.
    """
    doc_id = models.CharField(max_length=26, primary_key=True)


class QueryTerm(models.Model):
    """Model to store query terms used to generate random queries

    See management commands gatherqueryterms and weighted_queries.
    """
    term = models.CharField(max_length=26, primary_key=True)

    def __str__(self):
        return self.term

    def __eq__(self, other):
        return self.term == other.term
