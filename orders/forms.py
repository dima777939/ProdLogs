from django.forms import ModelForm
from django.shortcuts import get_object_or_404

from .models import OrderLog, Order, Operation
from django import forms

ITERATION_OPERATIONS = [
    "gruboe-volochenie",
    "liniya-70",
    "lentoobmotka",
]

BUHTOVKA = [
    "buhtovka",
]


class OrderLogForm(ModelForm):
    def __init__(self, *args, **data):
        super(OrderLogForm, self).__init__(*args, **data)
        if len(self.initial) and data:
            self.fields["order"].queryset = Order.objects.filter(
                id=data["initial"]["order"].id
            )
        self.fields["iteration"].widget = forms.HiddenInput()
        self.form_for_buhtovka(data) if len(data) else None
        self.get_hidden_fields(data) if len(data) else None

    id_order_log = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = OrderLog
        fields = [
            "order",
            "operation",
            "operator",
            "color_cores",
            "prev_number_container",
            "container",
            "number_container",
            "total_in_meters",
            "comment",
            "iteration",
        ]

    def get_operation(self, data):
        if len(self.initial):
            operation = data["initial"]["operation"]
        else:
            operation_id = [
                val
                for field in data.values()
                for key, val in field.items()
                if key == "operation"
            ]
            operation = get_object_or_404(Operation, id=operation_id[0])
        return operation

    def form_for_buhtovka(self, data):
        operation = self.get_operation(data)
        if operation.slug in BUHTOVKA:
            self.fields["color_cores"].initial = "б/ц"
            self.fields["container"].initial = "бух"
            self.fields["number_container"].label = "Кол-во бухт"
            self.fields["total_in_meters"].label = "Метраж бухты"

    def get_hidden_fields(self, data):
        operation = self.get_operation(data)
        hidden_field_3 = ["gruboe-volochenie", "bolshaya-skrutka", "lentoobmotka"]
        hidden_field_2 = ["liniya-90", "buhtovka"]
        hidden_field_1 = ["liniya-70"]
        if operation.slug in hidden_field_3:
            self.fields["color_cores"].widget = forms.HiddenInput()
            self.fields["prev_number_container"].widget = forms.HiddenInput()
            self.fields["container"].widget = forms.HiddenInput()
        elif operation.slug in hidden_field_2:
            self.fields["color_cores"].widget = forms.HiddenInput()

        elif operation.slug in hidden_field_1:
            self.fields["prev_number_container"].widget = forms.HiddenInput()
            self.fields["container"].widget = forms.HiddenInput()

    def clean_total_in_meters(self):
        cd = self.cleaned_data
        order = cd["order"]
        operation = cd["operation"]
        total_meters = cd["total_in_meters"]
        order_log_meter = OrderLog.objects.filter(
            order=order, operation=operation
        ).values_list("total_in_meters", flat=True)
        order_total_meter = sum(order_log_meter) + cd["total_in_meters"]
        if operation.slug in ITERATION_OPERATIONS:
            # Проверка на превышение длинны
            if int(order.footage) + 200 < total_meters:
                raise forms.ValidationError(
                    f"Метраж указан больше чем в заказе. Длинна заказа {order.footage} м."
                )
            # Проверка, если длинна меньше требуемой
            elif int(order.footage) - 200 > total_meters:
                raise forms.ValidationError(
                    f"Указанная длинна меньше длинны заказа. Длинна заказа {order.footage} м."
                )
        elif operation.slug in BUHTOVKA:
            len_bight = cd["number_container"]
            order_log_meter = OrderLog.objects.filter(
                order=order, operation=operation
            ).values_list("total_in_meters", "number_container")
            if order_log_meter:
                order_total_meter = sum(map(lambda x: x[0] * x[1], order_log_meter))
            if total_meters > 200:
                raise forms.ValidationError(f"Длинна бухты не должна превышать 200 м.")
            elif int(order.footage) + 200 < total_meters * len_bight:
                raise forms.ValidationError(
                    f"Превышение общей длинны заказа. Заказ {order.footage}м. Выход {len_bight * total_meters}м. Бухта {len_bight}м. Длинна бухт {total_meters}м."
                )
            elif (
                (int(order.footage) + 200)
                - (order_total_meter + (len_bight * total_meters))
            ) < 0:
                raise forms.ValidationError(
                    f"Метраж указан больше чем в заказе. Длинна заказа {order.footage} м. Остаток {order.footage - order_total_meter}"
                )
        else:
            # Проверка обшей длинны заказа при делении заказа на барабаны
            if (int(order.footage) + 200) - order_total_meter < 0:
                raise forms.ValidationError(
                    f"Метраж указан больше чем в заказе. Длинна заказа {order.footage} м. Остаток {order.footage - (sum(order_log_meter))}"
                )
        return cd["total_in_meters"]

    def clean_number_container(self):
        cd = self.cleaned_data
        number_container = cd["number_container"]
        order = cd["order"]
        operation = cd["operation"]
        # Проверка номера катушки
        if number_container > 250 and operation.slug not in BUHTOVKA:
            raise forms.ValidationError("Проверь номер катушки")
        num_containers_in_operation = OrderLog.objects.filter(
            order=order, operation=operation
        ).values_list("number_container", flat=True)
        # Проверка на дублирование номера катушки
        if (
            number_container in num_containers_in_operation
            and operation.slug not in BUHTOVKA
        ):
            raise forms.ValidationError(
                f"Катушка №{number_container} уже присутствует в заказе"
            )
        return cd["number_container"]
