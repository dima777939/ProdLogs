# Generated by Django 2.2 on 2021-07-15 04:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0003_auto_20210714_1303'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='in_production',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='productionorders',
            name='finished',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Готов'),
        ),
        migrations.AlterField(
            model_name='order',
            name='discard',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Брак'),
        ),
        migrations.AlterField(
            model_name='order',
            name='finished',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Готов'),
        ),
        migrations.CreateModel(
            name='OrderLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color_cores', models.CharField(choices=[('бел', 'белый'), ('син', 'синий'), ('крс', 'красный'), ('чер', 'черный'), ('ж/з', 'жел-зелен'), ('б/ц', 'нет')], max_length=3, verbose_name='Цвет жилы')),
                ('container', models.CharField(max_length=3, verbose_name='Тара')),
                ('number_container', models.PositiveSmallIntegerField(verbose_name='Номер тары')),
                ('total_in_meters', models.PositiveSmallIntegerField(verbose_name='Метраж/Кол-во')),
                ('date_finished', models.DateField(auto_now_add=True, verbose_name='Дата')),
                ('iteration', models.PositiveSmallIntegerField(blank=True)),
                ('otk', models.BooleanField(db_index=True, default=False)),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.Operation', verbose_name='Операция')),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Оператор')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='log', to='orders.Order', verbose_name='Заказ')),
            ],
        ),
    ]
