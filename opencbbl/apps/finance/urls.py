from django.urls import path
from . import views

urlpatterns = [
    path('', views.finance_index, name='finance_index'),
    path('operations/', views.finance_operations, name='finance_operations'),
    path('operations/add/', views.finance_operation_add, name='finance_operation_add'),
    path('operations/delete/<int:pk>/', views.finance_operation_delete, name='finance_operation_delete'),
    path('operations/export/', views.finance_export_excel, name='finance_export_excel'),
    path('statistics/', views.finance_statistics, name='finance_statistics'),
    path('documents/', views.documents_index, name='documents_index'),
    path('documents/<slug:slug>/', views.documents_category, name='documents_category'),
    path('documents/<slug:category_slug>/upload/', views.document_upload, name='document_upload'),
    path('documents/delete/<int:pk>/', views.document_delete, name='document_delete'),
]
