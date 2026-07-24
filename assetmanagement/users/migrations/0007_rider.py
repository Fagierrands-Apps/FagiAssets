from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_add_qr_token_to_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rider_id', models.CharField(blank=True, editable=False, max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('id_number', models.CharField(max_length=50, unique=True)),
                ('plate_number', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['rider_id'],
            },
        ),
    ]
