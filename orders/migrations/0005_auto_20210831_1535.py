# Generated by Django 2.2 on 2021-08-31 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20210715_1108'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderlog',
            options={'ordering': ('date_finished',), 'verbose_name': 'Log операции', 'verbose_name_plural': 'Список операций'},
        ),
        migrations.AddField(
            model_name='productionorders',
            name='count_tara',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='batch_number',
            field=models.IntegerField(db_index=True, unique=True, verbose_name='Номер партии'),
        ),
        migrations.AlterField(
            model_name='order',
            name='in_production',
            field=models.BooleanField(db_index=True, default=False, verbose_name='В производстве'),
        ),
        migrations.AlterField(
            model_name='orderlog',
            name='container',
            field=models.CharField(choices=[('ж/б', 'ж/б'), ('д/б', 'д/б'), ('бух', 'бухта')], max_length=3, verbose_name='Тара'),
        ),
        migrations.AlterField(
            model_name='orderlog',
            name='iteration',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
    ]