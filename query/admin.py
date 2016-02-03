from django.contrib import admin
from query.models import Query, DayStatistic, StopWord, Pillar, Newspaper


class DayStatisticAdmin(admin.ModelAdmin):
    list_display = ('date', 'count', 'checked')


class StopWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'user', 'query')
    search_fields = ['word']
    list_filter = ('user', 'query')


class NewspaperAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_date', 'end_date', 'editions', 'pillar')
    search_fields = ['title']
    list_filter = ('pillar', )


admin.site.register(Query)
admin.site.register(DayStatistic, DayStatisticAdmin)
admin.site.register(StopWord, StopWordAdmin)
admin.site.register(Pillar)
admin.site.register(Newspaper, NewspaperAdmin)

