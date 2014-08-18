import json

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

    
    def get_query_dict(self):
        """Return a JSON serializable representation of the query object, that 
        contains all relevant data and metadata.
        """
        excl_art_types = [a.art_type for a in self.exclude_article_types.all()]
        excl_distr = [d.distribution for d in self.exclude_distributions.all()]

        return {
            'query_id': self.id,
            'query': self.query,
            'date_lower': str(self.date_lower),
            'date_upper': str(self.date_upper),
            'exclude_article_types': excl_art_types, 
            'exclude_distributions': excl_distr, 
            'comment': self.comment,
            'date_created': str(self.date_created)
        }


    def __unicode__(self):
        return self.query


class DayStatistic( models.Model ):
    """DayStatistic is used to generate timeline graphs. Data for the
    DayStatistic table is gathered with the 'gatherstatistics' management
    command.
    """
    date    = models.DateField( unique = True )
    count   = models.IntegerField()
    checked = models.DateTimeField( auto_now = True )


    def __unicode__( self ):
        return '{}: {}'.format(str(self.date), self.count) 
