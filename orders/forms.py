from django.forms import ModelForm, CharField
from .models import OrderLog


class OrderLogForm(ModelForm):
    # operator = CharField(initial=False)

    class Meta:
        model = OrderLog
        fields = ['order', 'operation', 'operator', 'color_cores', 'container',
                  'number_container', 'total_in_meters']
