from django.forms import ModelForm, ModelChoiceField, Textarea
from .models import OrderLog, Order, Operation
from manufactur.models import User
from django import forms


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