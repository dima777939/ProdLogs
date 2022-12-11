from django import forms
from orders.models import Operation, Order
from manufactur.models import User

from bootstrap_datepicker_plus.widgets import DatePickerInput


class ManePageSearchForm(forms.Form):

    search_text = forms.CharField(
        min_length=4, max_length=10, label="Номер партии", required=False
    )


class AdvancedSearchForm(forms.Form):
    DESIGN_CHOICE = [
        ("", "--------"),
        ("нг", "круглый"),
        ("Пнг", "плоский"),
    ]
    PURPOSE_CHOICE = [
        ("", "--------"),
        ("LS", "LS"),
        ("LTx", "LTx"),
        ("FRLS", "FRLS"),
        ("FRLSLTx", "FRLSLTx"),
    ]
    CORES_CHOICE = [
        ("", "--------"),
        (1, "1 жила"),
        (2, "2 жилы"),
        (3, "3 жилы"),
        (4, "4 жилы"),
        (5, "5 жил"),
    ]
    CROSSSECTION_CHOICE = [
        ("", "--------"),
        ("0.5", "0.5 мм"),
        ("0.75", "0.75 мм"),
        ("1.0", "1.0 мм"),
        ("1.5", "1.5 мм"),
        ("2.5", "2.5 мм"),
        ("4.0", "4.0 мм"),
        ("6.0", "6.0 мм"),
        ("10", "10 мм"),
    ]

    batch_number = forms.IntegerField(
        min_value=0000, max_value=9999, required=False, label="Номер партии"
    )
    operation = forms.ModelChoiceField(
        queryset=Operation.objects.all(), required=False, label="Операция"
    )
    operator = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True), required=False, label="Оператор"
    )
    start_date = forms.DateField(widget=DatePickerInput(),required=False, label="Дата начало")
    end_date = forms.DateField(widget=DatePickerInput(),required=False, label="Дата конец")
    design = forms.ChoiceField(
        choices=DESIGN_CHOICE, required=False, label="Исполнение"
    )
    purpose = forms.ChoiceField(
        choices=PURPOSE_CHOICE, required=False, label="Назначение"
    )
    cores = forms.ChoiceField(choices=CORES_CHOICE, required=False, label="Кол-во жил")
    crosssection = forms.ChoiceField(
        choices=CROSSSECTION_CHOICE, required=False, label="Сечение жилы"
    )
    finished = forms.BooleanField(initial=False, required=False, label="Готов")
    discard = forms.BooleanField(initial=False, required=False, label="Забракован")

    def clean(self):
        cd = super(AdvancedSearchForm, self).clean()
        for value in cd.values():
            if value:
                return cd
        raise forms.ValidationError("Не выбран ни один параметр")