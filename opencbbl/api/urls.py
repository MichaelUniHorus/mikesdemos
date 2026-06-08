from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, ThemaViewSet, OrganizationViewSet, LocationViewSet

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'themas', ThemaViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'locations', LocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
