# Generated by Django 4.0.3 on 2022-04-26 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackersite', '0028_user_demo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='demo',
            new_name='demo_user',
        ),
    ]