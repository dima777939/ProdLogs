from django.db import models
from django.urls import reverse


from manufactur.models import User
from .fields import OrderingField


class Operation(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(max_length=50, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тех операция"
        verbose_name_plural = "Тех операции"

    def get_absolute_url(self):
        return reverse("orders:order_list_by_category", args=[self.slug])


class Order(models.Model):
    PLASTIC_CHOICE = [
        ("ВВГ", "ВВГ"),
        ("ППГ", "ППГ"),
    ]
    DESIGN_CHOICE = [
        ("нг", "нг"),
        ("Пнг", "Пнг"),
    ]
    PURPOSE_CHOICE = [
        ("LS", "LS"),
        ("LTx", "LTx"),
        ("FRLS", "FRLS"),
        ("FRLSLTx", "FRLSLTx"),
    ]
    CORES_CHOICE = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]
    CROSSSECTION_CHOICE = [
        ("0.5", "0.5"),
        ("0.75", "0.75"),
        ("1.0", "1.0"),
        ("1.5", "1.5"),
        ("2.5", "2.5"),
        ("4.0", "4.0"),
        ("6.0", "6.0"),
        ("10", "10"),
    ]

    batch_number = models.IntegerField(
        verbose_name="Номер партии", unique=True, db_index=True
    )
    slug = models.SlugField(max_length=10, db_index=True)
    operation = models.ForeignKey(
        Operation,
        related_name="order_operation",
        on_delete=models.CASCADE,
        default=1,
        verbose_name="Операция",
        db_index=True,
    )
    plastic = models.CharField(
        max_length=3, verbose_name="Пластик", choices=PLASTIC_CHOICE, default="ВВГ"
    )
    design = models.CharField(
        max_length=3, verbose_name="Исполнение", choices=DESIGN_CHOICE, default="нг"
    )
    purpose = models.CharField(
        max_length=7, verbose_name="Назначение", choices=PURPOSE_CHOICE, default="LS"
    )
    cores = models.IntegerField(verbose_name="Количество жил", choices=CORES_CHOICE)
    crosssection = models.CharField(
        max_length=4, verbose_name="Поперечное сечение", choices=CROSSSECTION_CHOICE
    )
    footage = models.IntegerField(verbose_name="Метраж", default=15000)
    created = models.DateTimeField(verbose_name="Дата добавления", auto_now_add=True)
    completion = models.DateField(verbose_name="Дата завершения")
    updated = models.DateField(verbose_name="Дата обновления", auto_now=True)
    finished = models.BooleanField(verbose_name="Готов", default=False, db_index=True)
    discard = models.BooleanField(verbose_name="Брак", default=False, db_index=True)
    in_production = models.BooleanField(
        default=False, db_index=True, verbose_name="В производстве"
    )

    class Meta:
        ordering = (
            "operation",
            "batch_number",
        )
        index_together = (("batch_number", "slug"),)
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return (
            f"№{self.batch_number} {self.operation} {self.plastic} {self.design} {self.purpose} "
            f"{self.cores}x{self.crosssection}  {self.footage} м."
        )

    def get_absolute_url(self):
        return reverse("orders:order_detail", args=[self.id, self.slug])


class ProductionOrders(models.Model):
    order = models.ForeignKey(
        Order, related_name="production", on_delete=models.PROTECT, verbose_name="Заказ"
    )
    ordering = OrderingField(blank=True, for_field="order")
    count_tara = models.PositiveSmallIntegerField(blank=True, default=0)
    comment = models.CharField(max_length=200, verbose_name="Комментарий")
    finished = models.BooleanField(default=False, verbose_name="Готов", db_index=True)

    class Meta:
        ordering = ("ordering",)
        verbose_name = "Заказ в производство"
        verbose_name_plural = "Заказы в производство"

    def __str__(self):
        return self.order.__str__()


class OrderLog(models.Model):
    COLOR_CORES_CHOICE = [
        ("бел", "белый"),
        ("син", "синий"),
        ("крс", "красный"),
        ("чер", "черный"),
        ("ж/з", "жел-зелен"),
        ("б/ц", "нет"),
    ]
    CONTAINER_CHOICE = [
        ("ж/б", "ж/б"),
        ("д/б", "д/б"),
        ("бух", "бухта"),
    ]

    order = models.ForeignKey(
        Order,
        related_name="log",
        on_delete=models.PROTECT,
        verbose_name="Заказ",
        db_index=True,
    )
    operation = models.ForeignKey(
        Operation, on_delete=models.PROTECT, verbose_name="Операция", db_index=True
    )
    operator = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name="Оператор", db_index=True
    )
    color_cores = models.CharField(
        max_length=3,
        choices=COLOR_CORES_CHOICE,
        default="б/ц",
        verbose_name="Цвет жилы",
    )
    container = models.CharField(
        max_length=3,
        choices=CONTAINER_CHOICE,
        default="ж/б",
        verbose_name="Приемный барабан",
    )
    prev_container = models.CharField(
        max_length=3,
        choices=CONTAINER_CHOICE,
        default="ж/б",
        verbose_name="Отдающий барабан",
        blank=True,
        null=True,
    )
    number_container = models.PositiveIntegerField(verbose_name="№ тары")
    prev_number_container = models.PositiveSmallIntegerField(
        verbose_name="№ тары отдающей"
    )
    total_in_meters = models.PositiveSmallIntegerField(verbose_name="Метраж")
    date_finished = models.DateField(auto_now_add=True, verbose_name="Дата")
    iteration = models.PositiveSmallIntegerField(blank=True, default=0)
    comment = models.CharField(max_length=1000, verbose_name="Комментарий", blank=True)
    otk = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ("date_finished",)
        verbose_name = "Log операции"
        verbose_name_plural = "Лог операций"

    def __str__(self):
        return self.order.__str__()

    def get_absolut_url(self):
        return reverse("orders:order_log", args=[self.order.id])
