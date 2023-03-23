from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View


from orders.models import Order, ProductionOrders
from .shelf import Shelf
from .forms import ShelfAddOrderForm, ShelfAddCommentForm
from actions.services import ActionUser


class ShelfAddView(LoginRequiredMixin, View):
    def post(self, request):
        if request.is_ajax():
            order_id = request.POST.get("id")
            action = request.POST.get("action")
            if order_id and action:
                try:
                    shelf = Shelf(request)
                    order = get_object_or_404(Order, id=order_id)
                    if action == "add":
                        shelf.add(order)
                    else:
                        shelf.remove(order)
                    return JsonResponse({"status": "ok", "order": order_id})
                except Order.DoesNotExist:
                    return JsonResponse({"status": "except"})
            return HttpResponse("Такого заказа не существует")
        return HttpResponse("Можно добавлять только кнопкой 'В работу'")


class ShelfAddTimeOrderView(View):
    def post(self, request, order_id):
        shelf = Shelf(request)
        order = get_object_or_404(Order, id=order_id)
        form = ShelfAddOrderForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            shelf.update_time(order=order, time=cd["time"], update_time=cd["update"])
            if cd["update"]:
                return redirect("shelf:shelf_detail")
        return redirect("orders:order_list")


class ShelfRemoveView(View):
    def get(self, request, order_id):
        shelf = Shelf(request)
        order = get_object_or_404(Order, id=order_id)
        shelf.remove(order)
        return redirect(reverse("shelf:shelf_detail"))

    def post(self, request, order_id):
        shelf = Shelf(request)
        form = ShelfAddCommentForm(request.POST)
        order = get_object_or_404(Order, id=order_id)
        if form.is_valid():
            cd = form.cleaned_data
            shelf.add_comment(order=order, comment=cd["comment"])
            return redirect("shelf:shelf_detail")


class ShelfDetailView(PermissionRequiredMixin, View):
    permission_required = "orders.add_productionorders"

    def get(self, request):
        shelf = Shelf(request)
        for item in shelf:
            item["update_time_form"] = ShelfAddOrderForm(
                initial={"time": item["time"], "update": True}
            )
            item["comment_form"] = ShelfAddCommentForm(
                initial={"comment": item["comment"]}
            )
        return render(request, "shelf/shelf_detail.html", {"shelf": shelf})


class ShelfGetView(PermissionRequiredMixin, View):
    permission_required = "orders.add_productionorders"

    def get(self, request):
        shelf = Shelf(request)
        for item in shelf:
            ProductionOrders.objects.create(
                order=item["order"], comment=item["comment"]
            )
            Order.objects.filter(id=item["order"].id).update(in_production=True)
        shelf.clear()
        ActionUser(
            request.user,
            f"Добавил заказы в производство: {len(shelf)} шт.",
            type_target="follow",
        ).create_actions()
        return redirect(reverse("shelf:shelf_detail"))
