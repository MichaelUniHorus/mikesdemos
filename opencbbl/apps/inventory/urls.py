from django.urls import path
from . import views

urlpatterns = [
    path('', views.component_list, name='component_list'),
    path('add/', views.component_add, name='component_add'),
    path('<int:pk>/edit/', views.component_edit, name='component_edit'),
    path('<int:pk>/delete/', views.component_delete, name='component_delete'),
    path('assembled/', views.assembled_pc_list, name='assembled_pc_list'),
    path('assembled/add/', views.assembled_pc_add, name='assembled_pc_add'),
    path('assembled/<int:pk>/', views.assembled_pc_detail, name='assembled_pc_detail'),
    path('assembled/<int:pk>/disassemble/', views.assembled_pc_disassemble, name='assembled_pc_disassemble'),
]
