# Generated by Django 4.0.1 on 2022-04-05 21:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trackersite', '0015_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='creator',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='time_created',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
