from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_alter_organization_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.TextField(blank=True, null=True, verbose_name='Название организации'),
        ),
    ]
