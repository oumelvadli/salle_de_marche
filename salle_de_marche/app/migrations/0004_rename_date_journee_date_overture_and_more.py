# Generated by Django 4.2.6 on 2024-04-03 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_journee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='journee',
            old_name='date',
            new_name='date_overture',
        ),
        migrations.RemoveField(
            model_name='journee',
            name='ouvert',
        ),
        migrations.AddField(
            model_name='journee',
            name='date_fermeture',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='journee',
            name='est_ouvert',
            field=models.BooleanField(default=False),
        ),
    ]
