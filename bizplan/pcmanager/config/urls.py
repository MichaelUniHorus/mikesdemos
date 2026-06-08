from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from apps.accounts import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('builds/', include('apps.builds.urls')),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
]
