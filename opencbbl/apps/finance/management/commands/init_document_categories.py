from django.core.management.base import BaseCommand
from apps.finance.models import DocumentCategory

class Command(BaseCommand):
    help = 'Create default document categories'

    def handle(self, *args, **kwargs):
        categories = [
            ('Учредительные документы', 'founding', 'Устав, документы регистрации и др.', 1),
            ('Внутренние документы', 'internal', 'Договоры, приказы, внутренние регламенты', 2),
            ('Финансовые документы', 'financial', 'Банковские выписки, счета, чеки', 3),
        ]

        for name, slug, description, order in categories:
            cat, created = DocumentCategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': description, 'order': order}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
            else:
                self.stdout.write(f'Category already exists: {name}')

        self.stdout.write(self.style.SUCCESS('Document categories initialized'))
