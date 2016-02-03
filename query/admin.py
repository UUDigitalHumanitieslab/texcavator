from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from query.models import Query, DayStatistic, StopWord, Pillar, Newspaper


class AugmentedUserAdmin(UserAdmin):
    """ Enables filtering users by group. """
    list_filter = UserAdmin.list_filter + ('groups__name',)


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


admin.site.unregister(User)
admin.site.register(User, AugmentedUserAdmin)
admin.site.register(Query)
admin.site.register(DayStatistic, DayStatisticAdmin)
admin.site.register(StopWord, StopWordAdmin)
admin.site.register(Pillar)
admin.site.register(Newspaper, NewspaperAdmin)

