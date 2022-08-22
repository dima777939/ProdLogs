from django.urls import path
from . import views

app_name = "shelf"

urlpatterns = [
    path("", views.ShelfDetailView.as_view(), name="shelf_detail"),
    path("add/", views.ShelfAddView.as_view(), name="shelf_add"),
    path(
        "remove/<int:order_id>/", views.ShelfRemoveView.as_view(), name="shelf_remove"
    ),
    path("get/", views.ShelfGetView.as_view(), name="shelf_get"),
    path("add_time/<int:order_id>", views.ShelfAddTimeOrderView.as_view(), name="shelf_add_time_order")
]
