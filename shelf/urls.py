from django.urls import path
from . import views

app_name = "shelf"

urlpatterns = [
    path("", views.ShelfDetailView.as_view(), name="shelf_detail"),
    path("add/<int:order_id>/", views.ShelfAddView.as_view(), name="shelf_add"),
    path(
        "remove/<int:order_id>/", views.ShelfRemoveView.as_view(), name="shelf_remove"
    ),
    path("get/", views.ShelfGetView.as_view(), name="shelf_get"),
]
