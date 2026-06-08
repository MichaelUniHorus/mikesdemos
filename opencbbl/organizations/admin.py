from django.contrib import admin
from .models import Region, Thema, Organization, Location


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name_ru', 'okato', 'name_en']
    search_fields = ['name_ru', 'name_en']


@admin.register(Thema)
class ThemaAdmin(admin.ModelAdmin):
    list_display = ['name_ru', 'thema_id']
    search_fields = ['name_ru', 'name_en']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'region', 'cbr_date_added']
    list_filter = ['region', 'thema', 'cbr_date_added']
    search_fields = ['name', 'inn', 'address']
    readonly_fields = ['cbr_id', 'created_at', 'updated_at']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['address', 'organization', 'latitude', 'longitude', 'is_geocoded']
    list_filter = ['is_geocoded']
    search_fields = ['address', 'organization__name']
    readonly_fields = ['created_at', 'updated_at']
