from django.core.management.base import BaseCommand
from django.conf import settings
from organizations.services import CBRAPIService
from organizations.models import Location


class Command(BaseCommand):
    help = 'Geocode all locations without coordinates using Yandex API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--region',
            type=str,
            help='Filter by region name (e.g., "Алтайский край")',
        )
        parser.add_argument(
            '--api-key',
            type=str,
            help='Yandex Geocoder API key (or set YANDEX_GEOCODER_API_KEY in .env)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset is_geocoded flag for all locations in region',
        )

    def handle(self, *args, **options):
        region_filter = options.get('region')
        api_key = options.get('api_key') or getattr(settings, 'YANDEX_GEOCODER_API_KEY', None)
        reset = options.get('reset')
        
        if not api_key:
            self.stdout.write(self.style.ERROR(
                'Yandex Geocoder API key required. '
                'Provide it with --api-key or set YANDEX_GEOCODER_API_KEY in .env'
            ))
            return
        
        # Reset is_geocoded flag if requested
        if reset:
            locations_to_reset = Location.objects.all()
            if region_filter:
                locations_to_reset = locations_to_reset.filter(address__icontains=region_filter)
            
            count = locations_to_reset.update(is_geocoded=False, latitude=None, longitude=None)
            self.stdout.write(self.style.SUCCESS(f'Reset {count} locations'))
        
        self.stdout.write('Starting geocoding...')
        
        try:
            locations = Location.objects.filter(is_geocoded=False)
            
            if region_filter:
                locations = locations.filter(address__icontains=region_filter)
            
            total = locations.count()
            self.stdout.write(f'Found {total} locations without coordinates (filter: {region_filter or "none"})')
            
            if total == 0:
                self.stdout.write(self.style.WARNING('No locations to geocode'))
                return
            
            processed = CBRAPIService.geocode_all_locations(api_key, region_filter=region_filter)
            
            self.stdout.write(self.style.SUCCESS(
                f'Geocoding completed: {processed} locations processed'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during geocoding: {str(e)}'))
