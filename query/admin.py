from django.contrib import admin
from query.models import Query, DayStatistic


class DayStatisticAdmin( admin.ModelAdmin ):
	list_display = ( 'date', 'count', 'checked' )


admin.site.register(Query)
admin.site.register(DayStatistic, DayStatisticAdmin)
