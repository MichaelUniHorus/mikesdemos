from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0008_alter_organization_name'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP INDEX IF EXISTS organizations_organization_name_537540_idx;",
            reverse_sql="",
        ),
    ]
