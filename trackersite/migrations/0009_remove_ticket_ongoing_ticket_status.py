# Generated by Django 4.0.1 on 2022-04-04 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackersite', '0008_alter_project_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='ongoing',
        ),
        migrations.AddField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Open', 'Open'), ('Resolved', 'Rslvd'), ('In Progress', 'Prgrs')], default='New', max_length=11),
        ),
    ]
