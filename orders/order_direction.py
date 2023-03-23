from itertools import groupby

from django.shortcuts import get_object_or_404

from .models import Order, Operation, ProductionOrders, OrderLog


class OrderDirection:
    DESIGN_CABLE_CHECK = {
        "нг": {
            (
                "LS",
                "LTx",
            ): {
                "gruboe-volochenie": "liniya-70",
                "liniya-70": "bolshaya-skrutka",
                "bolshaya-skrutka": "liniya-90",
                "liniya-90": "buhtovka",
                "buhtovka": "otk",
            },
            (
                "FRLS",
                "FRLSLTx",
            ): {
                "gruboe-volochenie": "lentoobmotka",
                "lentoobmotka": "liniya-70",
                "liniya-70": "bolshaya-skrutka",
                "bolshaya-skrutka": "liniya-90",
                "liniya-90": "buhtovka",
                "buhtovka": "otk",
            },
        },
        "Пнг": {
            (
                "LS",
                "LTx",
            ): {
                "gruboe-volochenie": "liniya-70",
                "liniya-70": "liniya-90",
                "liniya-90": "buhtovka",
                "buhtovka": "otk",
            },
            (
                "FRLS",
                "FRLSLTx",
            ): {
                "gruboe-volochenie": "lentoobmotka",
                "lentoobmotka": "liniya-70",
                "liniya-70": "bolshaya-skrutka",
                "bolshaya-skrutka": "liniya-90",
                "liniya-90": "buhtovka",
                "buhtovka": "otk",
            },
        },
    }
    FINISH_OPERATIONS = ["buhtovka"]

    def get_previous_operation(self, order_id, operation):
        order = get_object_or_404(ProductionOrders, id=order_id)
        design = order.order.design
        purpose = order.order.purpose
        get_design = self.DESIGN_CABLE_CHECK.get(design, self.DESIGN_CABLE_CHECK["нг"])
        for key, value in get_design.items():
            if purpose in key:
                for prev, oper in value.items():
                    if oper == operation.slug:
                        return prev

    @staticmethod
    def allow_next_operation(order_in_prod):
        count_tara = order_in_prod.order.cores
        count_iter = order_in_prod.count_tara
        if int(count_tara) > int(count_iter) + 1:
            order_in_prod.count_tara += 1
            order_in_prod.save()
            return True

    @staticmethod
    def check_container(order_log_form):
        id_order_log = order_log_form.cleaned_data["id_order_log"]
        if id_order_log:
            container_in_log = get_object_or_404(OrderLog, id=id_order_log)
            container_in_log.iteration += 1
            container_in_log.save()

    @staticmethod
    def division_order(order_prod, order_log, order_in_prod):
        order_in_prod.count_tara += order_log.total_in_meters
        residual = order_prod.footage - order_in_prod.count_tara
        order_in_prod.comment += (
            f" Добавлено {order_log.total_in_meters} м. Остаток {residual} м. /"
        )
        order_in_prod.save()

    def next_operation(self, order_prod, operation_slug):
        # Удаление заказа с производства
        ProductionOrders.objects.filter(
            order=order_prod, order__operation__slug=operation_slug, finished=False
        ).update(finished=True)
        # Перевод заказа в таблице Order на след операцию
        design = order_prod.design
        purpose = order_prod.purpose
        get_design = self.DESIGN_CABLE_CHECK.get(design, self.DESIGN_CABLE_CHECK["нг"])
        for key in get_design.keys():
            if purpose in key:
                get_operation = get_design[key].get(operation_slug, operation_slug)
                operation = get_object_or_404(Operation, slug=get_operation)
                Order.objects.filter(id=order_prod.id).update(
                    operation=operation,
                    in_production=False,
                    finished=self.check_finished(operation_slug),
                )

    @staticmethod
    def buhtovka(order_prod, order_log, order_in_prod):
        len_bights = order_log.number_container * order_log.total_in_meters
        order_in_prod.count_tara += len_bights
        residual = order_prod.footage - order_in_prod.count_tara
        order_in_prod.comment += (
            f"Сделано {order_log.number_container} бухт по {order_log.total_in_meters} м."
            f" Остаток {residual} м. /  "
        )
        order_in_prod.save()

    @staticmethod
    def get_query_order_log(order_log_values):
        order_log_values_group = groupby(
            order_log_values, key=lambda number: number["number_container"]
        )
        order_log_group = [
            {number: [query for query in queryset]}
            for number, queryset in order_log_values_group
        ]
        return order_log_group

    def check_finished(self, slug):
        return True if slug in self.FINISH_OPERATIONS else False
