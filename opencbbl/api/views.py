from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from organizations.models import Region, Thema, Organization, Location
from .serializers import RegionSerializer, ThemaSerializer, OrganizationSerializer, LocationSerializer


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_ru', 'name_en']


class ThemaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Thema.objects.all()
    serializer_class = ThemaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_ru', 'name_en']


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization__region', 'organization__thema', 'is_geocoded', 'address', 'organization__sign']
    search_fields = ['address', 'organization__name', 'organization__inn']
    
    @action(detail=False, methods=['get'])
    def map_points(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(latitude__isnull=False, longitude__isnull=False, is_geocoded=True)
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['region', 'thema']
    search_fields = ['name', 'inn', 'address']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Organization.objects.count()
        locations_count = Location.objects.count()
        with_coords = Location.objects.filter(latitude__isnull=False, longitude__isnull=False, is_geocoded=True).count()
        by_region = Location.objects.values('organization__region__name_ru').annotate(
            total_locations=models.Count('id'),
            with_coords=models.Count('id', filter=models.Q(latitude__isnull=False, longitude__isnull=False, is_geocoded=True))
        )
        by_thema = Location.objects.values('organization__thema__name_ru').annotate(count=models.Count('id'))
        
        return Response({
            'total': total,
            'locations': locations_count,
            'with_coordinates': with_coords,
            'by_region': list(by_region),
            'by_thema': list(by_thema)
        })
    
    @action(detail=False, methods=['get'])
    def geocoding_stats(self, request):
        """Get geocoding statistics by region"""
        by_region = Location.objects.values('organization__region__name_ru').annotate(
            total_locations=models.Count('id'),
            with_coords=models.Count('id', filter=models.Q(latitude__isnull=False, longitude__isnull=False, is_geocoded=True))
        ).order_by('-total_locations')
        
        return Response(list(by_region))
