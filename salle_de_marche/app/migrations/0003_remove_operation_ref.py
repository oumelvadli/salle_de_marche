# Generated by Django 5.0.2 on 2024-03-13 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_operation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='operation',
            name='ref',
        ),
    ]
