from django.contrib import admin
from query.models import Query, DayStatistic, StopWord, Pillar, Newspaper, Period


class PeriodInline(admin.TabularInline):
    model = Period
    max_num = 2


@admin.register(DayStatistic)
class DayStatisticAdmin(admin.ModelAdmin):
    list_display = ('date', 'distribution', 'article_type', 'count', 'checked', )
    ordering = ['date', 'distribution', 'article_type']


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    inlines = [PeriodInline]
    list_display = ('title', 'query', 'user', 'date_modified')
    list_filter = ('user', )
    ordering = ['user', '-date_modified']


@admin.register(StopWord)
class StopWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'user', 'query', )
    search_fields = ['word']
    list_filter = ('user', )
    ordering = ['user', 'query', 'word']


@admin.register(Newspaper)
class NewspaperAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_date', 'end_date', 'editions', 'pillar', )
    search_fields = ['title']
    list_filter = ('pillar', )
    ordering = ['id']


@admin.register(Pillar)
class PillarAdmin(admin.ModelAdmin):
    pass
