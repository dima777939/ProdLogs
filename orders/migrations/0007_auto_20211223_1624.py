# Generated by Django 2.2 on 2021-12-23 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20211215_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlog',
            name='date_finished',
            field=models.DateField(auto_now_add=True, verbose_name='Дата'),
        ),
    ]
