from django.db import models


class DocID(models.Model):
    doc_id = models.CharField(max_length=26, primary_key=True)


class QueryTerm(models.Model):
    term = models.CharField(max_length=26, primary_key=True)


    def __str__(self):
        return self.term


    def __eq__(self, other):
        return self.term == other.term
