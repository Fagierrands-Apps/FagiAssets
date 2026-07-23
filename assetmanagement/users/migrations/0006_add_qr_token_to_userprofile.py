import uuid
from django.db import migrations, models


def assign_qr_tokens(apps, schema_editor):
    UserProfile = apps.get_model('users', 'UserProfile')
    for profile in UserProfile.objects.filter(qr_token=None):
        profile.qr_token = uuid.uuid4()
        profile.save(update_fields=['qr_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_migrate_to_fge_employee_ids'),
    ]

    operations = [
        # Step 1: add column as nullable
        migrations.AddField(
            model_name='userprofile',
            name='qr_token',
            field=models.UUIDField(null=True, unique=True, editable=False),
        ),
        # Step 2: backfill all existing rows with unique UUIDs
        migrations.RunPython(assign_qr_tokens, migrations.RunPython.noop),
        # Step 3: enforce non-null
        migrations.AlterField(
            model_name='userprofile',
            name='qr_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
