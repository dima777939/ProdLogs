from django.contrib import admin
from .models import Operation, Order, ProductionOrders, OrderLog


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "batch_number",
        "slug",
        "operation",
        "plastic",
        "design",
        "purpose",
        "cores",
        "crosssection",
        "footage",
        "completion",
        "finished",
        "discard",
        "in_production",
    ]
    list_filter = [
        "operation",
        "design",
        "purpose",
        "cores",
        "crosssection",
        "finished",
        "discard",
        "in_production",
    ]
    list_editable = ["footage", "operation", "finished", "discard", "crosssection", "in_production"]
    prepopulated_fields = {"slug": ("batch_number", "crosssection")}
    search_fields = ("batch_number",)

@admin.register(ProductionOrders)
class ProductionOrdersAdmin(admin.ModelAdmin):
    list_display = ["order", "comment", "finished"]
    list_filter = ["finished"]
    list_editable = ["finished"]
    search_fields = ("order__batch_number",)


@admin.register(OrderLog)
class OrderLofAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "operator",
        "operation",
        "color_cores",
        "container",
        "number_container",
        "total_in_meters",
        "date_finished",
        "otk",
    ]
    list_filter = ["order", "operator", "operation", "date_finished", "otk"]
    list_editable = [
        "operator",
        "color_cores",
        "total_in_meters",
        "number_container",
        "container",
    ]
    search_fields = ("order__batch_number",)
