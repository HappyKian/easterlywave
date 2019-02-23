from django.contrib import admin
from daterange_filter.filter import DateRangeFilter
from .models import AnnualStat, DailyStat

class PercipFilter(admin.SimpleListFilter):

    title = '雨量'
    parameter_name = 'percip'

    def lookups(self, request, model_admin):
        return (('storm', '暴雨'),)

    def queryset(self, request, queryset):
        if self.value() == 'storm':
            return queryset.filter(percip__gte=50)
        else:
            return queryset

# Register your models here.
@admin.register(AnnualStat)
class AnnualStatAdmin(admin.ModelAdmin):
    list_filter = ('year',)

@admin.register(DailyStat)
class DailyStatAdmin(admin.ModelAdmin):
    list_filter = ('name', ('date', DateRangeFilter))
