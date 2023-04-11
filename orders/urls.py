from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.OrderListListView.as_view(), name="order_list"),
    path("upload", views.OrderDataUploadView.as_view(), name="order_upload"),
    path(
        "production/detail/<slug:operation>/<int:order_id>/",
        views.ProdOrderDetailView.as_view(),
        name="order_prod_detail",
    ),
    path(
        "production/ordering/",
        views.OrderProductionOrderingView.as_view(),
        name="order_p_ordering",
    ),
    path("production/ordering/discard/all", views.OrderDiscardListView.as_view(), name="order_discard_all"),
    path(
        "production/discard/order/<int:orderlog_id>/<int:discard>/<str:shelf>",
        views.OrderOtkView.as_view(),
        name="order_discard",
    ),
    path(
        "production/discard/<int:order_id>",
        views.OrderOtkListView.as_view(),
        name="order_discard_list",
    ),
    path(
        "production/<slug:operation_slug>/",
        views.ProductionOrderView.as_view(),
        name="order_p_list",
    ),
    path(
        "production/<slug:operation_slug>/<int:id_open_form>/<int:num_container>/<str:id_order_log>",
        views.ProductionOrderView.as_view(),
        name="order_p_id",
    ),
    path("production/finish", views.OrderFinish.as_view(), name="orders_finish"),
    path(
        "<slug:operation_slug>/",
        views.OrderListListView.as_view(),
        name="order_list_by_category",
    ),
    path("<int:id>/<slug:slug>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("log/<int:order_id>", views.OrderLogView.as_view(), name="order_log"),
]
