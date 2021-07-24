from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    TEAM = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
    )

    t_number = models.PositiveIntegerField(verbose_name='Табельный номер', default='1', unique=True)
    team = models.IntegerField(choices=TEAM, default=0, verbose_name='Смена')
    is_master = models.BooleanField(verbose_name='Мастер', default=False)
    rough_drawing = models.BooleanField(verbose_name='Грубое волочение', default=False)
    fine_drawing = models.BooleanField(verbose_name='Тонкое волочение', default=False)
    frls = models.BooleanField(verbose_name='Лентообмотка', default=False)
    yl_300 = models.BooleanField(verbose_name='Автобухтовка 300', default=False)
    yl_600 = models.BooleanField(verbose_name='Автобухтовка 600', default=False)
    yl_1250 = models.BooleanField(verbose_name='Перемотка 1250', default=False)
    yl_450 = models.BooleanField(verbose_name='Ручная бухтовка 450', default=False)
    l_70 = models.BooleanField(verbose_name='Линия 70', default=False)
    l_90 = models.BooleanField(verbose_name='Линия 90', default=False)
    wild_twist = models.BooleanField(verbose_name='Маленькая скрутка', default=False)
    twist = models.BooleanField(verbose_name='Большая скрутка', default=False)
    armoring = models.BooleanField(verbose_name='Бронирование', default=False)
    packaging = models.BooleanField(verbose_name='Упаковка', default=False)
    otk = models.BooleanField(verbose_name='ОТК', default=False)

    def __str__(self):
        return self.first_name

 #   def get_absolute_url(self):
 #       return reverse()