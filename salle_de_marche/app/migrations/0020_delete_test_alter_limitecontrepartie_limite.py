# Generated by Django 5.0.6 on 2024-06-06 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_alter_operation_limite'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Test',
        ),
        migrations.AlterField(
            model_name='limitecontrepartie',
            name='limite',
            field=models.IntegerField(),
        ),
    ]
