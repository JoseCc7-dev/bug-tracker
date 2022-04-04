# Generated by Django 4.0.1 on 2022-04-04 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackersite', '0010_alter_ticket_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='priority',
            field=models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Urgent', 'Urgent')], default='Low', max_length=6),
        ),
    ]
