from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from .models import Order, Operation, ProductionOrders, OrderLog
from .forms import OrderLogForm
from shelf.forms import ShelfAddOrderForm
from .order_direction import OrderDirection as OD


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
    BUHTOVKA = [
        'buhtovka',
    ]
    LINE_OPERATIONS = [
        'bolshaya-skrutka',
        'liniya-90',
    ]

    def get(self, request, operation_slug, id_open_form=None):
        operator = request.user
        operation = get_object_or_404(Operation, slug=operation_slug)
        if id_open_form:
            order_in_prod = get_object_or_404(ProductionOrders, id=id_open_form, finished=False)
            data = {'order': order_in_prod.order, 'operation': operation, 'operator': operator}
            order_in_prod_form = OrderLogForm(initial=data)
            return render(request, 'orders/order_production_in_operation.html', {'operation': operation,
                                                                            'order_in_prod_form': order_in_prod_form,
                                                                            'operator': operator})
        operations = Operation.objects.all()
        orders_in_prod = ProductionOrders.objects.filter(finished=False, order__operation=operation)
        order_in_prod_form = OrderLogForm()
        return render(request, 'orders/order_production_list.html', {'operation': operation,
                                                                     'orders_in_prod': orders_in_prod,
                                                                     'operator': operator, 'operations': operations,
                                                                     'order_in_prod_form': order_in_prod_form,
                                                                     'ITERATION_OPERATIONS': self.ITERATION_OPERATIONS})

    def post(self, request, operation_slug):
        order_log_form = OrderLogForm(data=request.POST)
        # Валидация формы
        if order_log_form.is_valid():
            # Сохранение данных в таблицу из формы
            order_log = order_log_form.save()
            order_prod = get_object_or_404(Order, id=order_log.order.id)
            order_in_prod = get_object_or_404(ProductionOrders, order=order_prod, finished=False)
            # Сколько в заказе сделано катушек
            if operation_slug in self.ITERATION_OPERATIONS:
                if OD.allow_next_operation(order_in_prod):
                    return redirect(reverse('orders:order_p_list', args=[order_prod.operation.slug]))
            # Бухтова
            elif operation_slug in self.BUHTOVKA and (order_prod.footage - (order_log.total_in_meters *
                                                        order_log.number_container + order_in_prod.count_tara)) > 20:
                OD.buhtovka(order_prod, order_log, order_in_prod)
                return redirect(reverse('orders:order_p_list', args=[order_prod.operation.slug]))
            # Деление заказа по метражу на барабанах
            elif operation_slug in self.LINE_OPERATIONS and (order_prod.footage - (order_log.total_in_meters +
                                                                                   order_in_prod.count_tara)) > 100:
                OD.division_order(order_prod, order_log, order_in_prod)
                return redirect(reverse('orders:order_p_list', args=[order_prod.operation.slug]))
            OD.next_operation(OD, order_prod, operation_slug)
            return redirect(reverse('orders:order_p_list', args=[order_prod.operation.slug]))
        operation = get_object_or_404(Operation, slug=operation_slug)
        order_in_prod = get_object_or_404(Order, id=request.POST['order'])
        return render(request, 'orders/order_production_in_operation.html', {'order_in_prod_form': order_log_form,
                                                                              'operation': operation,
                                                                             })



class OrderDetailView(View):
    
    def get(self, request, id, slug):
        order = get_object_or_404(Order, id=id, slug=slug)
        return render(request, 'orders/orders_detail.html', {'order': order, })


class OrderFinish(View):

    def get(self, request):
        orders = Order.objects.filter(finished=True)
        return render(request, 'orders/order_finish_list.html', {'orders': orders})


class OrderLogView(View):

    def get(self, request, order_id):
        order_log = OrderLog.objects.filter(order_id=order_id)
        return render(request, 'orders/order_log.html', {'order_log': order_log})