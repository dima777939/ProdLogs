# Generated by Django 2.2 on 2021-06-04 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manufactur', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='t_number',
            field=models.PositiveIntegerField(verbose_name='Табельный номер'),
        ),
    ]
