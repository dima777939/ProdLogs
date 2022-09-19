from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderingField(models.PositiveIntegerField):
    def __init__(self, for_field=None, *args, **kwargs):
        self.for_field = for_field
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            try:
                qs = self.model.objects.filter(finished=False)
                query = getattr(model_instance, self.for_field).operation
                qs_filter = qs.filter(order__operation=query)
                # Номер последнего объекта
                last_item = qs_filter.latest(self.attname)
                value = last_item.ordering + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)
