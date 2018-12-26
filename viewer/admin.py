from django.contrib import admin
from daterange_filter.filter import DateRangeFilter
from .models import Station, HitRecord

# Register your models here.
admin.site.register(Station)

@admin.register(HitRecord)
class HitRecordAdmin(admin.ModelAdmin):
    list_filter = (('date', DateRangeFilter),)

