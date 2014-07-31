from django.db import models

from django.contrib.auth.models import User

class ArticleType(models.Model):
    art_type = models.CharField(max_length=30)

    def __unicode__(self):
        return self.art_type


class Distribution(models.Model):
    distribution = models.CharField(max_length=35)

    def __unicode__(self):
        return self.distribution


class Query(models.Model):
    query = models.TextField()
    date_lower = models.DateField()
    date_upper = models.DateField()
    exclude_article_types = models.ManyToManyField(ArticleType, blank=True)
    exclude_distributions = models.ManyToManyField(Distribution, blank=True)

    comment = models.TextField(blank=True)

    user = models.ForeignKey(User)

    date_created = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.query
