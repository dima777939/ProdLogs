from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from .models import Order, Operation, ProductionOrders, OrderLog
from .forms import OrderLogForm
from shelf.forms import ShelfAddOrderForm


class OrderListView(View):

    def get(self, request, operation_slug=None):
        operation = None
        operations = Operation.objects.all()
        orders = Order.objects.filter(finished=False, discard=False, in_production=False)
        shelf_order_form = ShelfAddOrderForm()
        if operation_slug:
            operation = get_object_or_404(Operation, slug=operation_slug)
            orders = orders.filter(operation=operation)
        return render(request, 'orders/orders_list.html', {'operation': operation, 'operations': operations,
                                                           'orders': orders, 'shelf_order_form': shelf_order_form})


class ProductionOrderView(View):
    ITERATION_OPERATIONS = [
        'gruboe-volochenie',
        'liniya-70',
        'lentoobmotka',
    ]
    NO_FRLS = {
        'gruboe-volochenie': 'liniya-70', 'liniya-70': 'bolshaya-skrutka', 'bolshaya-skrutka': 'liniya-90',
        'liniya-90': 'buhtovka'
    }
    FRLS = {
        'gruboe-volochenie': 'lentoobmotka', 'lentoobmotka': 'liniya-70', 'liniya-70': 'bolshaya-skrutka',
        'bolshaya-skrutka': 'liniya-90', 'liniya-90': 'buhtovka'
    }
    NO_FRLS_PNG = {
        'gruboe-volochenie': 'liniya-70', 'liniya-70': 'liniya-90', 'liniya-90': 'buhtovka'
    }
    DESIGN_CABLE_CHECK = {

    }

    def get(self, request, operation_slug, id_open_form=None):
        operator = request.user
        operation = get_object_or_404(Operation, slug=operation_slug)
        if id_open_form:
            order_in_prod = get_object_or_404(ProductionOrders, id=id_open_form)
            data = {'order': order_in_prod.order, 'operation': operation, 'operator': operator}
            order_in_prod_form = OrderLogForm(initial=data)
            return render(request, 'orders/order_production_form.html', {'order_in_prod_form': order_in_prod_form,
                                                                         'order_in_prod': order_in_prod})
        operations = Operation.objects.all()
        orders_in_prod = ProductionOrders.objects.filter(finished=False, order__operation=operation)
        order_in_prod_form = OrderLogForm()
        return render(request, 'orders/order_production_list.html', {'operation': operation,
                                                                     'orders_in_prod': orders_in_prod,
                                                                     'operator': operator, 'operations': operations,
                                                                     'order_in_prod_form': order_in_prod_form})

    def post(self, request, operation_slug):
        order_log_form = OrderLogForm(data=request.POST)
        # Валидация формы
        if order_log_form.is_valid():
            # Сохранение данных в таблицу из формы
            order_log = order_log_form.save()
            order_prod = get_object_or_404(Order, id=order_log.order.id)
            order_in_prod = get_object_or_404(ProductionOrders, order=order_prod)
            # Проверка заказа о переводе на следующую операцию
            if (operation_slug in self.ITERATION_OPERATIONS) or \
                    ((order_prod.footage - order_log.total_in_meters) > 100):
                count_order_in_log = OrderLog.objects.filter(order=order_log.order, operation=order_log.operation).count()
                count_iter = order_log.order.cores
                if int(count_iter) > int(count_order_in_log) or \
                    ((order_prod.footage - order_log.total_in_meters) > 100):
                    return redirect(reverse('orders:order_p_list', args=[order_prod.operation.slug]))
            # Удаление заказа с производства
            ProductionOrders.objects.filter(order=order_prod, order__operation__slug=operation_slug).delete()
            # Перевод заказа в таблице Order на след операцию
            # Круглый кабель
            if order_prod.design == 'нг' and order_prod.purpose in ['LS', 'LTx']:
                get_operation = self.NO_FRLS.get(operation_slug, operation_slug)
                operation = get_object_or_404(Operation, slug=get_operation)
                Order.objects.filter(id=order_prod.id).update(operation=operation, in_production=False)
            # Круглый кабель FRLS
            elif order_prod.design == 'нг' and order_prod.purpose in ['FRLS', 'FRLTx']:
                get_operation = self.NO_FRLS.get(operation_slug, operation_slug)
                operation = get_object_or_404(Operation, slug=get_operation)
                Order.objects.filter(id=order_prod.id).update(operation=operation, in_production=False)
            # Плоский кабель
            else:
                get_operation = self.NO_FRLS_PNG.get(operation_slug, operation_slug)
                operation = get_object_or_404(Operation, slug=get_operation)
                Order.objects.filter(id=order_prod.id).update(operation=operation, in_production=False)
            return redirect(reverse('orders:order_p_list', args=[order_prod.operation.slug]))


class OrderDetailView(View):
    
    def get(self, request, id, slug):
        order = get_object_or_404(Order, id=id, slug=slug)
        return render(request, 'orders/orders_detail.html', {'order': order, })


class OrderFinish(View):

    def get(self, request):
        orders = Order.objects.filter(finished=True)
        return render(request, 'orders/order_finish_list.html', {'orders': orders})
