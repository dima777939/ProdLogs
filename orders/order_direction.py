from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from .models import Order, Operation, ProductionOrders, OrderLog


class OrderDirection:

    DESIGN_CABLE_CHECK = {
        'нг': {
            ('LS', 'LSLTx',): {
                'gruboe-volochenie': 'liniya-70', 'liniya-70': 'bolshaya-skrutka', 'bolshaya-skrutka': 'liniya-90',
                'liniya-90': 'buhtovka', 'buhtovka': 'otk'
            },
            ('FRLS', 'FRLSLTx',): {
                'gruboe-volochenie': 'lentoobmotka', 'lentoobmotka': 'liniya-70', 'liniya-70': 'bolshaya-skrutka',
                'bolshaya-skrutka': 'liniya-90', 'liniya-90': 'buhtovka', 'buhtovka': 'otk'
            }
        },
        'Пнг': {
            ('LS', 'LSLTx', 'FRLS', 'FRLSLTx',): {
                'gruboe-volochenie': 'liniya-70', 'liniya-70': 'liniya-90', 'liniya-90': 'buhtovka', 'buhtovka': 'otk'
            }
        }
    }
    FINISH_OPERATIONS = ['buhtovka']


    @staticmethod
    def allow_next_operation(order_in_prod):
        count_tara = order_in_prod.order.cores
        count_iter = order_in_prod.count_tara
        if int(count_tara) > int(count_iter) + 1:
            order_in_prod.count_tara += 1
            order_in_prod.save()
            return True

    @staticmethod
    def division_order(order_prod, order_log, order_in_prod):
        order_in_prod.count_tara += order_log.total_in_meters
        residual = order_prod.footage - order_in_prod.count_tara
        order_in_prod.comment += f' Добавлено {order_log.total_in_meters} м. Остаток {residual} м. /'
        order_in_prod.save()

    def next_operation(self, order_prod, operation_slug):
        # Удаление заказа с производства
        ProductionOrders.objects.filter(order=order_prod, order__operation__slug=operation_slug,
                                        finished=False).update(finished=True)
        # Перевод заказа в таблице Order на след операцию
        design = order_prod.design
        purpose = order_prod.purpose
        get_design = self.DESIGN_CABLE_CHECK.get(design, self.DESIGN_CABLE_CHECK['нг'])
        for key in get_design.keys():
            if purpose in key:
                get_operation = get_design[key].get(operation_slug, operation_slug)
                operation = get_object_or_404(Operation, slug=get_operation)
                Order.objects.filter(id=order_prod.id).update(operation=operation, in_production=False,
                                     finished=True if order_prod.slug in self.FINISH_OPERATIONS else False)

    @staticmethod
    def buhtovka(order_prod, order_log, order_in_prod):
        len_bights = order_log.number_container * order_log.total_in_meters
        order_in_prod.count_tara += len_bights
        residual = order_prod.footage - order_in_prod.count_tara
        order_in_prod.comment += f'Сделано {order_log.number_container} бухт по {order_log.total_in_meters} м.' \
                                 f' Остаток {residual} м. /  '
        order_in_prod.save()
