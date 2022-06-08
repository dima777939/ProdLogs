from django.forms import ModelForm, ModelChoiceField, Textarea
from django.shortcuts import get_object_or_404

from .models import OrderLog, Order, Operation, ProductionOrders
from manufactur.models import User
from django import forms

ITERATION_OPERATIONS = [
        'gruboe-volochenie',
        'liniya-70',
        'lentoobmotka',
    ]

class OrderLogForm(ModelForm):

    def __init__(self, **data):
        super(OrderLogForm, self).__init__(**data)
        self.form_for_buhtovka() if len(data) else None

    class Meta:
        model = OrderLog
        fields = ['order', 'operation', 'operator', 'color_cores', 'container',
                  'number_container', 'total_in_meters']

    def form_for_buhtovka(self):
        if len(self.initial) and self.initial['operation'].slug == 'buhtovka':
            self.fields['color_cores'].initial = 'б/ц'
            self.fields['container'].initial = 'бух'
            self.fields['number_container'].label = 'Кол-во бухт'
            self.fields['total_in_meters'].label = 'Метраж бухты'

    def clean_number_container(self):
        cd = self.cleaned_data
        if cd["number_container"] > 250:
            raise forms.ValidationError("Проверь номер катушки")
        return cd["number_container"]

    def clean_total_in_meters(self):
        cd = self.cleaned_data
        order = cd["order"]
        operation = cd["operation"]

        order_log = OrderLog.objects.filter(order=order, operation=operation).values_list("total_in_meters", flat=True)
        order_total_meter = sum(order_log) + cd["total_in_meters"]
        if operation.slug in ITERATION_OPERATIONS:
            if int(order.footage) + 200 < cd["total_in_meters"]:
                raise forms.ValidationError(f"Метраж указан больше чем в заказе. Длинна заказа {int(order.footage)} м.")
            elif int(order.footage) - 200 > cd["total_in_meters"]:
                raise forms.ValidationError(f'Указанная длинна меньше длинны заказа. Длинна заказа {order.footage} м.')
        else:
            if int(order.footage) - order_total_meter < 0:
                raise forms.ValidationError(f"Метраж указан больше чем в заказе. Длинна заказа {int(order.footage)} м.")
        return cd["total_in_meters"]
