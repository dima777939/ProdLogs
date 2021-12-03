from django import forms
from orders.models import ProductionOrders


class ShelfAddOrderForm(forms.Form):
    ORDER_TIME_CHOICES = [(i, str(i)) for i in range(15, 195, 15)]

    time = forms.TypedChoiceField(choices=ORDER_TIME_CHOICES, coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class ShelfAddCommentForm(forms.Form):
    comment = forms.CharField(max_length=200)