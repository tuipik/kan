from django.contrib import admin

from map_sheet.models import MapSheet


class MapSheetAdmin(admin.ModelAdmin):
    list_display = ('name', 'scale', 'year')
    search_fields = ('name',)

admin.site.register(MapSheet, MapSheetAdmin)
