import json
from collections import defaultdict

from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User

from .tasks import write_newspaper_classification


class ArticleType(models.Model):
    """Model to store the names of article types that are available in the
    elasticsearch index.

    The article types are part of the metadata of a query.
    """
    id = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=35)

    def __unicode__(self):
        return self.id


class Distribution(models.Model):
    """Model that stores the names of distributions that are available in the
    elasticsearch index.

    The distributions are part of the metadata of a query.
    """
    id = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=35)

    def __unicode__(self):
        return self.id


class Pillar(models.Model):
    """Model that allows to store a categorization of Newspapers along Pillars."""
    name = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.name


class Newspaper(models.Model):
    """Model that stores the available Newspapers"""
    id = models.CharField(max_length=9, primary_key=True)
    title = models.CharField(max_length=500)
    start_date = models.DateField()
    end_date = models.DateField()
    editions = models.PositiveIntegerField()
    pillar = models.ForeignKey(Pillar, null=True)

    def __unicode__(self):
        return self.title


def update_newspaper_classification(sender, instance, created, **kwargs):
    """Updates the newspaper classification to be used both in Django as well as Celery"""
    classification = defaultdict(list)
    for newspaper in Newspaper.objects.all():
        if newspaper.pillar:
            classification[newspaper.pillar.id].append(newspaper.pk)
    classification_json = json.dumps(classification)
    write_newspaper_classification(classification_json)
    write_newspaper_classification.delay(classification_json)


signals.post_save.connect(update_newspaper_classification, sender=Newspaper)
signals.post_save.connect(update_newspaper_classification, sender=Pillar)


class Query(models.Model):
    """Model to store a User's queries.
    """
    title = models.CharField(max_length=100)
    comment = models.TextField(blank=True)
    query = models.TextField()
    nr_results = models.PositiveIntegerField(null=True)

    exclude_article_types = models.ManyToManyField(ArticleType, blank=True)
    exclude_distributions = models.ManyToManyField(Distribution, blank=True)
    selected_pillars = models.ManyToManyField(Pillar, blank=True)
    user = models.ForeignKey(User)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        """Make sure that Query titles are unique for a User"""
        unique_together = ('user', 'title')
        # Custom permissions
        permissions = (
            (
                'download_documents',
                'Can download results of a query',
            ),
            (
                'download_many_documents',
                'Can download larger numbers of results',
            ),
        )

    def get_query_dict(self):
        """Returns a JSON serializable representation of the query object, that
        contains all relevant data and metadata.
        """
        periods = Period.objects.filter(query=self)
        selected_dateranges = [{'lower': p.date_lower.isoformat(), 'upper': p.date_upper.isoformat()} for p in periods]
        excl_art_types = [a.id for a in self.exclude_article_types.all()]
        excl_distr = [d.id for d in self.exclude_distributions.all()]
        selected_pillars = [p.id for p in self.selected_pillars.all()]
        selected_pillar_names = [p.name for p in self.selected_pillars.all()]

        return {
            'pk': self.pk,
            'title': self.title,
            'query': self.query,
            'comment': self.comment,
            'nr_results': self.nr_results,
            'date_created': self.date_created.isoformat(),
            'dates': selected_dateranges,
            'exclude_article_types': excl_art_types,
            'exclude_distributions': excl_distr,
            'selected_pillars': selected_pillars,
            'selected_pillar_names': selected_pillar_names
        }

    def __unicode__(self):
        return self.query


class Period(models.Model):
    """Model to store the Periods for a Query"""
    date_lower = models.DateField()
    date_upper = models.DateField()
    query = models.ForeignKey(Query)


class DayStatistic(models.Model):
    """DayStatistic is used to generate timeline graphs. Data for the
    DayStatistic table is gathered with the 'gatherstatistics' management
    command.
    """
    date = models.DateField(unique=True)
    count = models.IntegerField()
    checked = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{}: {}'.format(str(self.date), self.count)


class StopWord(models.Model):
    """Model to store stopwords.

    Stopwords can be:

    - specific for a Query (applicable to a single User's Query, query/user != None)
    - specific for a User (applicable for all of a User's Queries, query == None, user != None)
    - non-specific/default (applicable to all Queries for all Users, user/query == None)
    """
    user = models.ForeignKey(User, null=True, blank=True)
    query = models.ForeignKey(Query, null=True, blank=True)
    word = models.CharField(max_length=100)

    def __unicode__(self):
        return self.word

    def get_stopword_dict(self):
        if self.user:
            user_name = self.user.username
        else:
            user_name = ''

        if self.query:
            query = self.query.title
        else:
            query = ''

        return {
            'id': self.id,
            'user': user_name,
            'query': query,
            'word': self.word
        }


class Term(models.Model):
    """Model to store frequencies and inverse document frequencies per term"""
    PRE_WWII = 'pre'
    WWII = 'WWII'
    POST_WWII = 'post'
    TIMEFRAME_CHOICES = (
        (PRE_WWII, 'pre-WWII: 1900-1940'),
        (WWII, 'WWII: 1940-1945'),
        (POST_WWII, 'post-WWII: 1945-1990'),
    )
    timeframe = models.CharField(max_length=4, choices=TIMEFRAME_CHOICES)
    word = models.CharField(max_length=200)
    count = models.PositiveIntegerField()
    idf = models.DecimalField(max_digits=7, decimal_places=4)

    class Meta:
        unique_together = (('timeframe', 'word'),)
