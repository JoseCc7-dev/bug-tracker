# Generated by Django 4.0.1 on 2022-04-08 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackersite', '0023_ticket_assigned_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='value_old',
            field=models.TextField(null=True),
        ),
    ]
