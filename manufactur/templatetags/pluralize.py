from django import template


register = template.Library()


@register.filter
def rupluralize(value, args=("заказ", "заказа", "заказов")):
    number = abs(int(value)) if str(value).isdigit() else 0
    a = number % 10
    b = number % 100

    if (a == 1) and (b != 11):
        return args[0]
    elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
        return args[1]
    else:
        return args[2]
