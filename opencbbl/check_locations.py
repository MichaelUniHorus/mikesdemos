import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opencbbl.settings')
django.setup()

from organizations.models import Location

print(f'Total locations: {Location.objects.count()}')
print(f'Altai Krai locations: {Location.objects.filter(address__icontains="Алтайский край").count()}')
print(f'Barnaul locations: {Location.objects.filter(address__icontains="Барнаул").count()}')
print(f'Biysk locations: {Location.objects.filter(address__icontains="Бийск").count()}')
