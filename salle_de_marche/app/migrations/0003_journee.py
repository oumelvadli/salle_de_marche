# Generated by Django 4.1.13 on 2024-03-27 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_operation_direction_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Journee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('ouvert', models.BooleanField(default=False)),
            ],
        ),
    ]
