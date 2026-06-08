import requests
import re
from django.conf import settings
from django.utils import timezone
from .models import Region, Thema, Organization, Location


class CBRAPIService:
    JSON_API_URL = 'https://www.cbr.ru/inside/warning-list/black-list-json'
    
    @staticmethod
    def _extract_region_from_address(address):
        """Extract region name from address string"""
        if not address:
            return None
        
        # Try to match region patterns (область, край, республика, АО)
        region_patterns = [
            r'([^,]*?(?:республика|область|край|АО)[^,]*)',
            r'([^,]*?(?:Республика|Область|Край|АО)[^,]*)'
        ]
        
        for pattern in region_patterns:
            match = re.search(pattern, address, re.IGNORECASE)
            if match:
                region_name = match.group(1).strip()
                # Normalize region name
                region_name = re.sub(r'[-–—]', ' ', region_name)
                region_name = re.sub(r'\s+', ' ', region_name).strip()
                return region_name
        
        return None
    
    @classmethod
    def fetch_all_organizations(cls, region_filter=None):
        """Fetch all organizations from CBR JSON API with bulk operations"""
        print(f"Fetching data from: {cls.JSON_API_URL}")
        response = requests.get(cls.JSON_API_URL)
        response.raise_for_status()
        data = response.json()
        
        total_count = len(data.get('RC', []))
        print(f"Total organizations in JSON: {total_count}")
        
        # Cache for regions and themas to avoid repeated queries
        region_cache = {}
        thema_cache = {}
        
        # Collect all organizations data first
        orgs_to_create = []
        orgs_to_update = []
        existing_cbr_ids = set(Organization.objects.values_list('cbr_id', flat=True))
        
        for idx, org_data in enumerate(data.get('RC', [])):
            # Filter by region if specified
            if region_filter and org_data.get('ADDR'):
                if region_filter.lower() not in org_data['ADDR'].lower():
                    continue
            
            if idx % 1000 == 0:
                print(f"[{idx+1}/{total_count}] Processing...")
            
            # Map Sign to Thema
            thema = None
            sign_text = org_data.get('Sign', '')
            if sign_text:
                if sign_text not in thema_cache:
                    thema, _ = Thema.objects.get_or_create(
                        name_ru=sign_text,
                        defaults={
                            'thema_id': hash(sign_text) % 100000,
                            'name_en': ''
                        }
                    )
                    thema_cache[sign_text] = thema
                thema = thema_cache[sign_text]
            
            # Extract region from address
            region = None
            addr_field = org_data.get('ADDR')
            if addr_field:
                region_name = cls._extract_region_from_address(addr_field)
                if region_name:
                    if region_name not in region_cache:
                        # Try to get existing region by name first
                        region = Region.objects.filter(name_ru=region_name).first()
                        if not region:
                            # Create new region with unique okato based on hash
                            region, _ = Region.objects.get_or_create(
                                name_ru=region_name,
                                defaults={
                                    'okato': abs(hash(region_name)) % 1000000,
                                    'name_en': ''
                                }
                            )
                        region_cache[region_name] = region
                    region = region_cache[region_name]
            
            org_dict = {
                'cbr_id': org_data['Id'],
                'name': org_data.get('Name', ''),
                'inn': org_data.get('INN', ''),
                'address': org_data.get('ADDR'),
                'website': org_data.get('Site'),
                'sign': org_data.get('Sign'),
                'is_closed': org_data.get('Closed', False),
                'comment': org_data.get('Comment'),
                'cbr_date_added': cls._parse_date(org_data.get('DT')),
                'cbr_date_updated': cls._parse_datetime(org_data.get('DateUpdate')),
                'org_type': org_data.get('OrgType'),
                'thema': thema,
                'region': region
            }
            
            if org_data['Id'] in existing_cbr_ids:
                orgs_to_update.append(org_dict)
            else:
                orgs_to_create.append(org_dict)
        
        print(f"Creating {len(orgs_to_create)} new organizations...")
        print(f"Updating {len(orgs_to_update)} existing organizations...")
        
        # Bulk create new organizations
        if orgs_to_create:
            Organization.objects.bulk_create([
                Organization(**org) for org in orgs_to_create
            ], batch_size=1000)
        
        # Bulk update existing organizations
        if orgs_to_update:
            print("Bulk updating organizations...")
            # Get existing organizations
            existing_orgs = Organization.objects.filter(cbr_id__in=[org['cbr_id'] for org in orgs_to_update])
            existing_org_map = {org.cbr_id: org for org in existing_orgs}
            
            # Prepare update data
            orgs_for_update = []
            for org_dict in orgs_to_update:
                org = existing_org_map.get(org_dict['cbr_id'])
                if org:
                    org.name = org_dict['name']
                    org.inn = org_dict['inn']
                    org.address = org_dict['address']
                    org.website = org_dict['website']
                    org.sign = org_dict['sign']
                    org.is_closed = org_dict['is_closed']
                    org.comment = org_dict['comment']
                    org.cbr_date_added = org_dict['cbr_date_added']
                    org.cbr_date_updated = org_dict['cbr_date_updated']
                    org.org_type = org_dict['org_type']
                    org.thema = org_dict['thema']
                    org.region = org_dict['region']
                    orgs_for_update.append(org)
            
            # Bulk update
            Organization.objects.bulk_update(
                orgs_for_update,
                ['name', 'inn', 'address', 'website', 'sign', 'is_closed', 
                 'comment', 'cbr_date_added', 'cbr_date_updated', 'org_type', 'thema', 'region'],
                batch_size=1000
            )
        
        # Process locations for all organizations
        print("Processing locations...")
        all_orgs = Organization.objects.filter(cbr_id__in=[org['cbr_id'] for org in orgs_to_create + orgs_to_update])
        org_map = {org.cbr_id: org for org in all_orgs}
        
        for org_data in data.get('RC', []):
            if region_filter and org_data.get('ADDR'):
                if region_filter.lower() not in org_data['ADDR'].lower():
                    continue
            
            org = org_map.get(org_data['Id'])
            if not org:
                continue
            
            addr_field = org_data.get('ADDR')
            if addr_field:
                addresses = cls._parse_addresses(addr_field)
                for addr in addresses:
                    addr_stripped = addr.strip()
                    if not Location.objects.filter(organization=org, address=addr_stripped).exists():
                        Location.objects.create(
                            organization=org,
                            address=addr_stripped,
                            is_geocoded=False
                        )
        
        return all_orgs
    
    @classmethod
    def sync_all_data(cls, region_filter=None):
        """Sync all data from CBR JSON API"""
        organizations = cls.fetch_all_organizations(region_filter=region_filter)
        
        return {
            'organizations': len(organizations)
        }
    
    @staticmethod
    def _parse_date(date_str):
        """Parse date string from CBR JSON API"""
        if not date_str:
            return None
        try:
            from datetime import datetime
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _parse_datetime(datetime_str):
        """Parse datetime string from CBR JSON API"""
        if not datetime_str:
            return None
        try:
            from datetime import datetime
            dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
            return timezone.make_aware(dt)
        except (ValueError, TypeError):
            try:
                from datetime import datetime
                dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
                return timezone.make_aware(dt)
            except (ValueError, TypeError):
                return None
    
    @staticmethod
    def _parse_addresses(addr_string):
        """Parse multiple addresses separated by semicolon"""
        if not addr_string:
            return []
        
        # Normalize line breaks and split by semicolon
        normalized = addr_string.replace('\r\n', ';').replace('\n', ';')
        addresses = normalized.split(';')
        
        # Clean up addresses
        cleaned_addresses = []
        for addr in addresses:
            addr = addr.strip()
            if addr:
                cleaned_addresses.append(addr)
        
        return cleaned_addresses
    
    @classmethod
    def geocode_address(cls, address, api_key, region_filter=None):
        """Geocode address using Yandex Geocoder API - returns results filtered by region"""
        try:
            url = 'https://geocode-maps.yandex.ru/1.x/'
            params = {
                'apikey': api_key,
                'geocode': address,
                'format': 'json',
                'results': 10  # Get up to 10 results per address
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if data.get('response') and data['response'].get('GeoObjectCollection'):
                features = data['response']['GeoObjectCollection'].get('featureMember', [])
                for feature in features:
                    geo_object = feature['GeoObject']
                    
                    # Filter by region if specified
                    if region_filter:
                        address_components = geo_object.get('metaDataProperty', {}).get('GeocoderMetaData', {}).get('Address', {}).get('Components', [])
                        region_found = False
                        for component in address_components:
                            if region_filter.lower() in component.get('name', '').lower():
                                region_found = True
                                break
                        if not region_found:
                            continue
                    
                    pos = geo_object['Point']['pos']
                    lon, lat = pos.split(' ')
                    results.append((float(lat), float(lon)))
            
            return results
        except Exception as e:
            print(f"  Error geocoding address '{address[:30]}...': {e}")
        
        return []
    
    @classmethod
    def geocode_all_locations(cls, api_key, region_filter=None):
        """Geocode all locations without coordinates - creates multiple locations for each result"""
        import time
        locations = Location.objects.filter(is_geocoded=False)
        
        if region_filter:
            locations = locations.filter(address__icontains=region_filter)
        
        total = locations.count()
        print(f"Geocoding {total} locations (filter: {region_filter or 'none'})...")
        
        total_processed = 0
        for idx, location in enumerate(locations):
            print(f"[{idx+1}/{total}] Geocoding: {location.address[:50]}...")
            results = cls.geocode_address(location.address, api_key, region_filter=region_filter)
            
            if results:
                # Update the original location with the first result
                location.latitude = results[0][0]
                location.longitude = results[0][1]
                location.is_geocoded = True
                location.save()
                print(f"  -> Main coordinates: {results[0][0]}, {results[0][1]}")
                
                # Create additional locations for other results
                for lat, lon in results[1:]:
                    new_location = Location.objects.create(
                        organization=location.organization,
                        address=location.address,
                        latitude=lat,
                        longitude=lon,
                        is_geocoded=True
                    )
                    print(f"  -> Additional coordinates: {lat}, {lon}")
                
                total_processed += len(results)
            else:
                print(f"  -> Failed to get coordinates")
            
            # Add delay to respect API rate limits
            time.sleep(0.5)
        
        return total_processed
