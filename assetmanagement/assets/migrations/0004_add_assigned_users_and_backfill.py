from django.db import migrations, models
from django.conf import settings


def backfill_assigned_users(apps, schema_editor):
    Asset = apps.get_model('assets', 'Asset')
    User = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])
    for asset in Asset.objects.exclude(assigned_to__isnull=True):
        # Add the legacy single user into the new M2M field
        asset.assigned_users.add(asset.assigned_to_id)


def remove_backfill(apps, schema_editor):
    # No-op: we don't want to remove relationships on reverse migration
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0003_auto_generate_asset_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='assigned_users',
            field=models.ManyToManyField(blank=True, related_name='assets', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(backfill_assigned_users, remove_backfill),
    ]