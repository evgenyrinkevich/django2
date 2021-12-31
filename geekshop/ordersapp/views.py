from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from mainapp.mixin import BaseClassContextMixin
from ordersapp.models import Order


class OrderListView(ListView, BaseClassContextMixin):
    model = Order
    title = 'Список заказов'


class OrderCreateView(CreateView, BaseClassContextMixin):
    pass


class OrderUpdateView(UpdateView, BaseClassContextMixin):
    pass


class OrderDeleteView(DeleteView, BaseClassContextMixin):
    pass


class OrderDetailView(DetailView, BaseClassContextMixin):
    model = Order
    title = 'Детали заказа'


def order_forming_complete(request, pk):
    pass
