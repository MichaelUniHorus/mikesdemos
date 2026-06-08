from django.contrib import admin
from .models import ComponentCategory, Component, AssembledPC, ActionLog

@admin.register(ComponentCategory)
class ComponentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'purchase_price', 'quantity', 'total_value', 'added_at']
    list_filter = ['category']
    search_fields = ['name', 'specs']
    readonly_fields = ['total_value', 'added_at', 'updated_at']

@admin.register(AssembledPC)
class AssembledPCAdmin(admin.ModelAdmin):
    list_display = ['title', 'quantity', 'cost_price', 'sale_price', 'profit', 'added_at']
    search_fields = ['title', 'notes']
    readonly_fields = ['cost_price', 'profit', 'added_at', 'updated_at']

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_name', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'object_name', 'description']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_name', 'description', 'timestamp']

