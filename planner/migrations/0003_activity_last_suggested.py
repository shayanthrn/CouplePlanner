# Generated by Django 5.1.1 on 2025-06-24 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_remove_activity_updated_at_activity_couple'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='last_suggested',
            field=models.DateField(blank=True, null=True),
        ),
    ]
