from datetime import time

import openpyxl
from django.http import HttpResponse
from django.utils import timezone

from orders.models import Order, OrderLog


class Search:
    order = Order
    orderlog = OrderLog

    def search_for_order(self, result_search):
        batch_number = result_search if result_search.isdigit() else None
        order = self.order.objects.filter(batch_number=batch_number)
        return order

    def search_for_orderlog(self, search_text):
        if search_text.isdigit() and len(search_text) < 7:
            order_logs = self.orderlog.objects.filter(
                order__batch_number=search_text
            ).select_related("order")
        else:
            order_logs = OrderLog.objects.filter(
                operator__last_name__icontains=search_text
            ).select_related("order", "operation", "operator")
        return order_logs


class AdvancedSearch:
    def __init__(self, cd):
        self.batch_number = cd["batch_number"] if cd["batch_number"] else None
        self.operation = cd["operation"] if cd["operation"] else None
        self.operator = cd["operator"] if cd["operator"] else None
        self.start_date = cd["start_date"] if cd["start_date"] else None
        self.end_date = cd["end_date"] if cd["end_date"] else None
        self.design = cd["design"] if cd["design"] else None
        self.purpose = cd["purpose"] if cd["purpose"] else None
        self.cores = cd["cores"] if cd["cores"] else None
        self.crosssection = cd["crosssection"] if cd["crosssection"] else None
        self.finished = cd["finished"]
        self.discard = cd["discard"]

    def get_orders_filter(self, export_to):
        orders = (
            self.search_for_orderlog()
            if self.operation
            or self.operator
            or export_to == "file"
            or self.start_date
            or self.end_date
            else self.search_for_order()
        )
        return orders

    def search_for_order(self):
        orders = Order.objects.filter(discard=self.discard, finished=self.finished)
        if self.batch_number:
            orders = orders.filter(batch_number=self.batch_number)
        if self.design:
            orders = orders.filter(design=self.design)
        if self.purpose:
            orders = orders.filter(purpose=self.purpose)
        if self.cores:
            orders = orders.filter(cores=self.cores)
        if self.crosssection:
            orders = orders.filter(crosssection=self.crosssection)
        return orders

    def search_for_orderlog(self):
        orderlog = (
            OrderLog.objects.filter(
                order__discard=self.discard, order__finished=self.finished
            )
            .select_related("operation", "order", "operator")
            .order_by("-date_finished")
        )
        if self.batch_number:
            orderlog = orderlog.filter(order__batch_number=self.batch_number)
        if self.operation:
            orderlog = orderlog.filter(operation=self.operation)
        if self.operator:
            orderlog = orderlog.filter(operator=self.operator)
        my_date = timezone.make_aware(
                    timezone.datetime.combine(self.start_date, time(hour=7)),
                    timezone.get_current_timezone(),
                )
        if self.start_date:
            orderlog = orderlog.filter(date_finished__gte=my_date)
        if self.end_date:
            orderlog = orderlog.filter(
                date_finished__lte=timezone.make_aware(
                    timezone.datetime.combine(self.end_date, time(hour=7)),
                    timezone.get_current_timezone(),
                )
            )
        if self.design:
            orderlog = orderlog.filter(order__design=self.design)
        if self.purpose:
            orderlog = orderlog.filter(order__purpose=self.purpose)
        if self.cores:
            orderlog = orderlog.filter(order__cores=self.cores)
        if self.crosssection:
            orderlog = orderlog.filter(order__crosssection=self.crosssection)
        return orderlog


class ExportExcel:
    def get_excel_response(self, orders) -> HttpResponse:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Orders"
        columns = [
            "Номер партии",
            "Операция",
            "Исполнитель",
            "Марка кабеля",
            "Метраж",
            "№ контейнера",
            "Дата",
            "Статус",
            "Последнее обновление",
        ]
        ws.append(columns)
        for order in orders:
            row = [
                order.order.batch_number,
                order.operation.__str__(),
                order.operator.__str__(),
                order.order.__str__(),
                order.total_in_meters,
                order.number_container,
                order.date_finished,
                self.get_status(order),
                order.order.updated,
            ]
            ws.append(row)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="orders_log.xlsx"'
        wb.save(response)
        return response

    @staticmethod
    def get_status(order):
        return "Готов" if order.order.finished else "На производстве"
