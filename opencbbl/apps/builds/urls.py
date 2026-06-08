from django.urls import path
from . import views

urlpatterns = [
    path('', views.kanban_view, name='kanban'),
    path('new/', views.build_add, name='build_add'),
    path('<int:pk>/', views.build_detail, name='build_detail'),
    path('<int:pk>/edit/', views.build_edit, name='build_edit'),
    path('<int:pk>/status/<str:status>/', views.build_change_status, name='build_change_status'),
]
