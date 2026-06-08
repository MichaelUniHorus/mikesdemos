from django.core.management.base import BaseCommand
from organizations.services import CBRAPIService


class Command(BaseCommand):
    help = 'Sync data from CBR Warning List JSON API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--region',
            type=str,
            help='Filter by region name (e.g., "Алтайский край")',
        )

    def handle(self, *args, **options):
        region_filter = options.get('region')
        
        if region_filter:
            self.stdout.write(f'Starting sync with CBR JSON API (filter: {region_filter})...')
        else:
            self.stdout.write('Starting sync with CBR JSON API...')
        
        try:
            result = CBRAPIService.sync_all_data(region_filter=region_filter)
            
            self.stdout.write(self.style.SUCCESS(
                f'Sync completed:\n'
                f'  - Organizations: {result["organizations"]}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during sync: {str(e)}'))
