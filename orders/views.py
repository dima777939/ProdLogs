from datetime import datetime, timedelta
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib import messages
from django.views.generic import ListView, FormView

from .models import Order, Operation, ProductionOrders, OrderLog
from .forms import OrderLogForm, UploadDataOrdersForm
from shelf.forms import ShelfAddOrderForm
from .order_direction import OrderDirection
from actions.services import ActionUser

OD = OrderDirection()

class OrderListListView(PermissionRequiredMixin, ListView):
    template_name = "orders/orders_list.html"
    paginate_by = 10
    context_object_name = "orders"
    shelf_order_form = ShelfAddOrderForm()
    operation = None
    queryset = Order.objects.filter(finished=False, discard=False, in_production=False)
    permission_required = "orders.view_order"

    def get_queryset(self):
        operation_slug = self.kwargs.get("operation_slug", None)
        if operation_slug:
            self.queryset = self.queryset.filter(operation__slug=operation_slug)
            self.operation = get_object_or_404(Operation, slug=operation_slug)
        return self.queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context["operation"] = self.operation
        context["operations"] = Operation.objects.all()
        context["shelf_order_form"] = self.shelf_order_form
        return context


class ProductionOrderView(PermissionRequiredMixin, View):
    permission_required = "orders.view_productionorders"

    ITERATION_OPERATIONS = [
        "gruboe-volochenie",
        "liniya-70",
        "lentoobmotka",
    ]
    BUHTOVKA = [
        "buhtovka",
    ]
    LINE_OPERATIONS = [
        "bolshaya-skrutka",
        "liniya-90",
    ]

    def get(
        self,
        request,
        operation_slug,
        id_open_form=None,
        num_container=None,
        id_order_log=None,
    ):
        operator = request.user
        operation = get_object_or_404(Operation, slug=operation_slug)
        if id_open_form:
            order_in_prod = get_object_or_404(
                ProductionOrders, id=id_open_form, finished=False
            )
            order = get_object_or_404(Order, id=order_in_prod.order.id)
            data = {
                "order": order,
                "operation": operation,
                "operator": operator,
                "prev_number_container": num_container,
                "id_order_log": id_order_log,
            }
            order_in_prod_form = OrderLogForm(initial=data)
            return render(
                request,
                "orders/order_production_in_operation.html",
                {
                    "operation": operation,
                    "order_in_prod_form": order_in_prod_form,
                    "operator": operator,
                },
            )
        operations = Operation.objects.all()
        orders_in_prod = ProductionOrders.objects.filter(
            finished=False, order__operation=operation
        )
        order_in_prod_form = OrderLogForm()
        return render(
            request,
            "orders/order_production_list.html",
            {
                "operation": operation,
                "orders_in_prod": orders_in_prod,
                "operator": operator,
                "operations": operations,
                "order_in_prod_form": order_in_prod_form,
                "ITERATION_OPERATIONS": self.ITERATION_OPERATIONS,
            },
        )

    def post(self, request, operation_slug):
        order_log_form = OrderLogForm(data=request.POST)
        # Валидация формы
        if order_log_form.is_valid():
            # Сохранение данных в таблицу из формы
            order_log = order_log_form.save(commit=False)
            order_prod = get_object_or_404(Order, id=order_log.order.id)
            order_in_prod = get_object_or_404(
                ProductionOrders, order=order_prod, finished=False
            )
            order_log = order_log_form.save()
            # Сколько в заказе сделано катушек
            if operation_slug in self.ITERATION_OPERATIONS:
                if OD.allow_next_operation(order_in_prod):
                    OD.check_container(order_log_form)
                    message = (
                        f"Операция: {order_prod.operation}. "
                        f"Сделал катушку №{order_log.number_container}.  Длинна - {order_log.total_in_meters} м. "
                        f"Катушка {order_in_prod.count_tara} из {order_prod.cores}."
                    )
                    ActionUser(
                        request.user,
                        message,
                        "iteration",
                        order_prod,
                    ).create_actions()
                    messages.success(
                        request,
                        f"Отлично, {request.user.first_name}. Заказ № {order_prod.batch_number}.  {message}. ",
                    )
                    return redirect(
                        reverse("orders:order_p_list", args=[order_prod.operation.slug])
                    )
            # Бухтова
            elif (
                operation_slug in self.BUHTOVKA
                and (
                    order_prod.footage
                    - (
                        order_log.total_in_meters * order_log.number_container
                        + order_in_prod.count_tara
                    )
                )
                > 20
            ):
                OD.buhtovka(order_prod, order_log, order_in_prod)
                message = (
                    f"Операция {order_prod.operation}. "
                    f"Сделал {order_log.number_container} бухт по {order_log.total_in_meters} м."
                )
                ActionUser(
                    request.user,
                    message,
                    "buhtovka",
                    order_prod,
                ).create_actions()
                messages.success(
                    request,
                    f"Отлично, {request.user.first_name}.   Заказ № {order_prod.batch_number}.  {message}",
                )
                return redirect(
                    reverse("orders:order_p_list", args=[order_prod.operation.slug])
                )
            # Деление заказа по метражу на барабанах
            elif (
                operation_slug in self.LINE_OPERATIONS
                and (
                    order_prod.footage
                    - (order_log.total_in_meters + order_in_prod.count_tara)
                )
                > 100
            ):
                OD.division_order(order_prod, order_log, order_in_prod)
                message = (
                    f"Операция {order_prod.operation}. "
                    f"На барабан №{order_log.number_container} намотано {order_log.total_in_meters} м. "
                    f"Остаток по длине заказа {order_prod.footage - order_in_prod.count_tara} м."
                )
                ActionUser(
                    request.user,
                    message,
                    "line_oper",
                    order_prod,
                ).create_actions()
                messages.success(
                    request,
                    f"Отлично, {request.user.first_name}.   Заказ № {order_prod.batch_number}.  {message}",
                )
                return redirect(
                    reverse("orders:order_p_list", args=[order_prod.operation.slug])
                )
            OD.next_operation(order_prod, operation_slug)
            message = f"Заказ {order_prod.batch_number} на операции {order_prod.operation} готов."
            ActionUser(
                request.user,
                message,
                "finish",
                order_prod,
            ).create_actions()
            messages.success(request, f"Отлично, {request.user.first_name}. {message}")
            return redirect(
                reverse("orders:order_p_list", args=[order_prod.operation.slug])
            )
        operation = get_object_or_404(Operation, slug=operation_slug)
        messages.error(
            request,
            f"Опечатался, {request.user.first_name} ? Проверь всё ли правильно.",
        )
        return render(
            request,
            "orders/order_production_in_operation.html",
            {
                "order_in_prod_form": order_log_form,
                "operation": operation,
            },
        )


class ProdOrderDetailView(View):
    ITERATION_OPERATIONS = [
        "gruboe-volochenie",
        "liniya-70",
        "lentoobmotka",
    ]
    BUHTOVKA = [
        "buhtovka",
    ]
    LINE_OPERATIONS = [
        "bolshaya-skrutka",
        "liniya-90",
    ]

    def get(self, request, order_id, operation):
        operation_obj = get_object_or_404(Operation, slug=operation)
        prev_operation_slug = OD.get_previous_operation(
            operation=operation_obj, order_id=order_id
        )
        operation_prev = get_object_or_404(Operation, slug=prev_operation_slug)
        order_prod = get_object_or_404(ProductionOrders, id=order_id)
        order_log_detail = OrderLog.objects.filter(
            order=order_prod.order, operation=operation_prev
        ).order_by("number_container", "total_in_meters")
        if operation in self.LINE_OPERATIONS or operation in self.BUHTOVKA:
            order_log_detail = order_log_detail.values()
            order_log_detail = OD.get_query_order_log(order_log_detail)
        return render(
            request,
            "orders/order_prod_detail.html",
            {
                "order_log_detail": order_log_detail,
                "operation": operation_obj,
                "order_prod_id": order_id,
                "order_prod": order_prod,
                "ITERATION_OPERATIONS": self.ITERATION_OPERATIONS,
                "LINE_OPERATIONS": self.LINE_OPERATIONS,
                "BUHTOVKA": self.BUHTOVKA,
            },
        )


class OrderDetailView(View):
    def get(self, request, id, slug):
        order = get_object_or_404(Order, id=id, slug=slug)
        return render(
            request,
            "orders/orders_detail.html",
            {
                "order": order,
            },
        )


class OrderFinish(View):
    def get(self, request):
        orders = Order.objects.filter(finished=True)
        return render(request, "orders/order_finish_list.html", {"orders": orders})


class OrderLogView(View):
    def get(self, request, order_id):
        order_log = OrderLog.objects.filter(order_id=order_id)
        return render(request, "orders/order_log.html", {"order_log": order_log})


class OrderProductionOrderingView(
    PermissionRequiredMixin, CsrfExemptMixin, JsonRequestResponseMixin, View
):
    permission_required = "orders.change_productionorders"

    def post(self, request):
        for id, ordering in self.request_json.items():
            ProductionOrders.objects.filter(id=id, finished=False).update(
                ordering=ordering
            )
        return self.render_json_response({"saved": "ok"})


class OrderDataUploadView(PermissionRequiredMixin, FormView, View):
    template_name = "orders/orders_upload.html"
    form_class = UploadDataOrdersForm
    success_url = reverse_lazy("orders:order_upload")
    permission_required = "orders.add_order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        context["file"] = self.get_file()
        return context

    @staticmethod
    def get_file():
        current_time = datetime.now() - timedelta(minutes=2)
        file = Order.objects.filter(created__gte=current_time)
        return file

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response({"form": form})

