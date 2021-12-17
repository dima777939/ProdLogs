from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('production/<slug:operation_slug>/', views.ProductionOrderView.as_view(), name='order_p_list'),
    path('production/<slug:operation_slug>/<int:id_open_form>/', views.ProductionOrderView.as_view(), name='order_p_id'),
    path('production/finish', views.OrderFinish.as_view(), name='orders_finish'),
    path('<slug:operation_slug>/', views.OrderListView.as_view(), name='order_list_by_category'),
    path('<int:id>/<slug:slug>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('log/<int:order_id>', views.OrderLogView.as_view(), name='order_log')
]
