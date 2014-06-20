from django.db import models


class DocID(models.Model):
    doc_id = models.CharField(max_length=26, primary_key=True)
