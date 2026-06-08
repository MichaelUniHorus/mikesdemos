from django.contrib import admin
from .models import PCBuild

@admin.register(PCBuild)
class PCBuildAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'cost_price', 'sale_price', 'profit', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'notes']
    readonly_fields = ['cost_price', 'profit', 'created_at', 'updated_at']
