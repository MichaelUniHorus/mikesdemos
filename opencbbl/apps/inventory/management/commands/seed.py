from django.core.management.base import BaseCommand
from apps.inventory.models import ComponentCategory, Component
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **kwargs):
        # Create categories
        categories_data = [
            ('Процессоры', 'cpu'),
            ('Видеокарты', 'gpu'),
            ('ОЗУ', 'ram'),
            ('SSD', 'ssd'),
            ('Охлаждение', 'cooler'),
            ('Корпуса', 'case'),
            ('Блоки питания', 'psu'),
            ('Материнские платы', 'motherboard'),
        ]

        for name, slug in categories_data:
            ComponentCategory.objects.get_or_create(name=name, slug=slug)

        self.stdout.write(self.style.SUCCESS('Categories created'))

        # Create sample components
        cpu_cat = ComponentCategory.objects.get(slug='cpu')
        gpu_cat = ComponentCategory.objects.get(slug='gpu')
        ram_cat = ComponentCategory.objects.get(slug='ram')
        ssd_cat = ComponentCategory.objects.get(slug='ssd')
        cooler_cat = ComponentCategory.objects.get(slug='cooler')
        case_cat = ComponentCategory.objects.get(slug='case')
        psu_cat = ComponentCategory.objects.get(slug='psu')
        mb_cat = ComponentCategory.objects.get(slug='motherboard')

        components_data = [
            (cpu_cat, 'Intel Core i3-10100F', '4 ядра, 3.7 ГГц', 5000, 5),
            (cpu_cat, 'Intel Core i5-10400F', '6 ядер, 2.9 ГГц', 7000, 3),
            (gpu_cat, 'NVIDIA GTX 1660', '6 ГБ GDDR5', 10000, 4),
            (gpu_cat, 'AMD RX 5700', '8 ГБ GDDR6', 12000, 2),
            (ram_cat, 'DDR4 16 ГБ (2x8)', '3200 МГц', 5000, 6),
            (ram_cat, 'DDR4 8 ГБ', '2666 МГц', 2500, 4),
            (ssd_cat, 'SSD 240 ГБ SATA', '2.5"', 2000, 8),
            (ssd_cat, 'SSD 480 ГБ SATA', '2.5"', 3500, 3),
            (cooler_cat, 'Башенный кулер', '4 heatpipes', 1500, 5),
            (cooler_cat, 'Кулер для Intel', 'LGA 1200', 1200, 4),
            (case_cat, 'MicroATX корпус', 'без блока питания', 1500, 6),
            (case_cat, 'ATX корпус', 'без блока питания', 2000, 3),
            (psu_cat, 'БП 550 Вт', '80+ Bronze', 2200, 5),
            (psu_cat, 'БП 650 Вт', '80+ Bronze', 2800, 3),
            (mb_cat, 'H410 LGA 1200', 'mATX', 3000, 4),
            (mb_cat, 'B460 LGA 1200', 'ATX', 4000, 2),
        ]

        for category, name, specs, price, qty in components_data:
            Component.objects.get_or_create(
                category=category,
                name=name,
                defaults={
                    'specs': specs,
                    'purchase_price': price,
                    'quantity': qty,
                }
            )

        self.stdout.write(self.style.SUCCESS('Components created'))

        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Admin user created (admin/admin123)'))
        else:
            self.stdout.write('Admin user already exists')

        self.stdout.write(self.style.SUCCESS('Seed completed'))
