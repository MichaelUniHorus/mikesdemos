from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0006_beneficiary_beneficiaryownership_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(blank=True, max_length=2000, null=True, verbose_name='Название организации'),
        ),
    ]
