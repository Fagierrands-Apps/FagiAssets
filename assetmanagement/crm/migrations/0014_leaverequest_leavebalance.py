from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0013_remove_employee_daily_target_employee_weekly_target'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[('annual', 'Annual'), ('sick', 'Sick'), ('emergency', 'Emergency'), ('unpaid', 'Unpaid')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('days_requested', models.IntegerField()),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('review_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='crm.employee')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_leaves', to='crm.employee')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LeaveBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annual_days_total', models.IntegerField(default=21)),
                ('annual_days_used', models.IntegerField(default=0)),
                ('sick_days_total', models.IntegerField(default=10)),
                ('sick_days_used', models.IntegerField(default=0)),
                ('year', models.IntegerField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='leave_balance', to='crm.employee')),
            ],
        ),
    ]
