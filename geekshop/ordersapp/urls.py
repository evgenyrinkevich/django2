from django.urls import path

from ordersapp.views import OrderListView, OrderCreateView, \
    OrderUpdateView, OrderDeleteView, OrderDetailView, order_forming_complete, order_change_status, \
    order_item_price_update

app_name = 'ordersapp'
urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('create/', OrderCreateView.as_view(), name='create'),
    path('update/<int:pk>/', OrderUpdateView.as_view(), name='update'),
    path('read/<int:pk>/', OrderDetailView.as_view(), name='read'),
    path('delete/<int:pk>/', OrderDeleteView.as_view(), name='delete'),
    path('forming_complete/<int:pk>/', order_forming_complete, name='forming_complete'),
    path('order_change_status/<int:pk>/', order_change_status, name='order_change_status'),

    path('order/update/price/<int:pk>/', order_item_price_update, name='order_price_update'),

]
