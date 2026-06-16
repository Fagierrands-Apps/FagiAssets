# Generated migration for adding daily_target field to Employee

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0011_alter_employee_role_handlerreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='daily_target',
            field=models.IntegerField(default=10, help_text='Daily call target for this employee'),
        ),
    ]
