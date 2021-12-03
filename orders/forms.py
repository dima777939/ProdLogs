from django.forms import ModelForm, ModelChoiceField, Textarea
from .models import OrderLog, Order, Operation
from manufactur.models import User
from django import forms


class OrderLogForm(ModelForm):
    order = ModelChoiceField(queryset=Order.objects.all())
    operator = ModelChoiceField(queryset=User.objects.all())
    operation = ModelChoiceField(queryset=Operation.objects.all())
    # order = forms.CharField(initial=Order.objects.all())
    # operator = forms.CharField(initial=User.objects.all())
    # operation = forms.CharField(initial=Operation.objects.all())

    class Meta:
        model = OrderLog
        fields = ['order', 'operation', 'operator', 'color_cores', 'container',
                  'number_container', 'total_in_meters']

#     def __init__(self, *args, **kwargs):
#         operator = kwargs.pop('operator', '')
#         order = kwargs.pop('order', '')
#         operation = kwargs.pop('operation', '')
#         super(OrderLogForm, self).__init__(*args, **kwargs)
#         self.fields['']
#
# class OrderForm(forms.Form):
#
#     order = forms.EmailField()