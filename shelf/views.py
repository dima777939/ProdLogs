from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from orders.models import Order, ProductionOrders
from .shelf import Shelf
from .forms import ShelfAddOrderForm


class ShelfAddView(View):

    def post(self, request, order_id):
        shelf = Shelf(request)
        order = get_object_or_404(Order, id=order_id)
        form = ShelfAddOrderForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            shelf.add(order=order, time=cd['time'], update_time=cd['update'])
            if cd['update']:
                return redirect('shelf:shelf_detail')
        return redirect('orders:order_list')


class ShelfRemoveView(View):

    def get(self, request, order_id):
        shelf = Shelf(request)
        order = get_object_or_404(Order, id=order_id)
        shelf.remove(order)
        return redirect(reverse('shelf:shelf_detail'))


class ShelfDetailView(View):

    def get(self, request):
        shelf = Shelf(request)
        for item in shelf:
            item['update_time_form'] = ShelfAddOrderForm(
                initial={'time': item['time'], 'update': True}
            )
        return render(request, 'shelf/shelf_detail.html', {'shelf': shelf})


class ShelfGetView(View):

    def get(self, request):
        shelf = Shelf(request)
        for item in shelf:
            ProductionOrders.objects.create(order=item['order'], comment=item['time'])
            Order.objects.filter(id=item['order'].id).update(in_production=True)
        shelf.clear()
        return redirect(reverse('shelf:shelf_detail'))