import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_rider'),
    ]

    operations = [
        migrations.AddField(
            model_name='rider',
            name='qr_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
