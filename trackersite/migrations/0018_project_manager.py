# Generated by Django 4.0.1 on 2022-04-05 21:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trackersite', '0017_remove_project_active_project_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='manager',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='project_manager', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
