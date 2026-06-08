from rest_framework import serializers
from organizations.models import Region, Thema, Organization, Location


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'okato', 'name_ru', 'name_en']


class ThemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thema
        fields = ['id', 'thema_id', 'name_ru', 'name_en']


class LocationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_inn = serializers.CharField(source='organization.inn', read_only=True)
    organization_sign = serializers.CharField(source='organization.sign', read_only=True)
    organization_website = serializers.CharField(source='organization.website', read_only=True, allow_null=True)
    region_name = serializers.CharField(source='organization.region.name_ru', read_only=True)
    region_id = serializers.IntegerField(source='organization.region.id', read_only=True)
    thema_name = serializers.CharField(source='organization.thema.name_ru', read_only=True)
    cbr_date_added = serializers.DateField(source='organization.cbr_date_added', read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(source='organization.updated_at', read_only=True, allow_null=True)
    is_closed = serializers.BooleanField(source='organization.is_closed', read_only=True)
    
    class Meta:
        model = Location
        fields = [
            'id', 'address', 'latitude', 'longitude', 'is_geocoded',
            'organization', 'organization_name', 'organization_inn',
            'organization_sign', 'organization_website', 'region_name', 'region_id', 'thema_name',
            'cbr_date_added', 'updated_at', 'is_closed'
        ]


class OrganizationSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name_ru', read_only=True)
    thema_name = serializers.CharField(source='thema.name_ru', read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'inn', 'address', 'website',
            'cbr_date_added', 'cbr_date_updated', 'is_closed',
            'region', 'thema', 'region_name', 'thema_name'
        ]
