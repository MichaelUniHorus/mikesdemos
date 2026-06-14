from django.contrib import admin
from .models import FinanceOperation, DocumentCategory, Document

@admin.register(FinanceOperation)
class FinanceOperationAdmin(admin.ModelAdmin):
    list_display = ['date', 'name', 'operation_type', 'payment_purpose', 'amount']
    list_filter = ['operation_type', 'date']
    search_fields = ['name', 'payment_purpose']

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'uploaded_at']
    list_filter = ['category']
