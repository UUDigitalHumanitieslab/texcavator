from django.contrib import admin
from query.models import Query, DayStatistic, StopWord


class DayStatisticAdmin(admin.ModelAdmin):
    list_display = ('date', 'count', 'checked')


class StopWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'user', 'query')
    search_fields = ['word']
    list_filter = ('user', 'query')

admin.site.register(Query)
admin.site.register(DayStatistic, DayStatisticAdmin)
admin.site.register(StopWord, StopWordAdmin)
