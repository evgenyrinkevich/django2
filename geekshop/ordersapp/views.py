from django.db import transaction
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from baskets.models import Basket
from mainapp.mixin import BaseClassContextMixin
from mainapp.models import Product
from ordersapp.forms import OrderItemsForm
from ordersapp.models import Order, OrderItem


class OrderListView(LoginRequiredMixin, ListView, BaseClassContextMixin):
    model = Order
    title = 'Список заказов'

    def get_queryset(self):
        return Order.objects.filter(is_active=True, user=self.request.user)


class OrderCreateView(LoginRequiredMixin, CreateView, BaseClassContextMixin):
    model = Order
    fields = []
    title = 'Создание заказа'
    success_url = reverse_lazy('orders:list')

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)

        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemsForm, extra=1)
        if self.request.POST:
            formset = OrderFormSet(self.request.POST)
        else:
            basket_item = Basket.objects.filter(user=self.request.user)
            if basket_item:
                OrderFormSet = inlineformset_factory(Order, OrderItem, OrderItemsForm, extra=basket_item.count())
                formset = OrderFormSet()
                for form, baskets in zip(formset.forms, basket_item):
                    form.initial['product'] = baskets.product
                    form.initial['quantity'] = baskets.quantity
                    form.initial['price'] = baskets.product.price
                basket_item.delete()
            else:
                formset = OrderFormSet()

        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            form.instance.user = self.request.user
            result = super().form_valid(form)
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

            if self.object.get_total_cost() == 0:
                self.object.delete()

        return result


class OrderUpdateView(LoginRequiredMixin, UpdateView, BaseClassContextMixin):
    model = Order
    fields = []
    title = 'Редактирование заказа'
    success_url = reverse_lazy('orders:list')

    def get_context_data(self, **kwargs):
        context = super(OrderUpdateView, self).get_context_data(**kwargs)

        OrderFormSet = inlineformset_factory(Order, OrderItem, OrderItemsForm, extra=1)
        if self.request.POST:
            formset = OrderFormSet(self.request.POST, instance=self.object, queryset=OrderItem.objects.select_related('product', 'product__category').all())
        else:
            formset = OrderFormSet(instance=self.object, queryset=OrderItem.objects.select_related('product', 'product__category').all())
            for form in formset:
                if form.instance.pk:
                    form.initial['price'] = form.instance.product.price

        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            result = super().form_valid(form)
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

            if self.object.get_total_cost() == 0:
                self.object.delete()

        return result


class OrderDeleteView(LoginRequiredMixin, DeleteView, BaseClassContextMixin):
    model = Order
    title = 'Удаление заказа'
    success_url = reverse_lazy('orders:list')


class OrderDetailView(LoginRequiredMixin, DetailView, BaseClassContextMixin):
    model = Order
    title = 'Детали заказа'


@login_required
def order_forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.SENT_TO_PROCEED
    order.save()
    return HttpResponseRedirect(reverse('orders:list'))


@login_required
def order_change_status(request, pk):
    """
    Переключает статус заказа
    """
    order = get_object_or_404(Order, pk=pk)
    status_dict = dict(Order.ORDER_STATUS_CHOICES)
    if order.status in (Order.READY, Order.CANCELED):
        order.status = Order.FORMING
    else:
        list_status = list(status_dict)
        result_index = list_status[list_status.index(order.status) + 1]
        order.status = result_index
    order.save()
    return HttpResponseRedirect(reverse('orders:list'))


def order_item_price_update(request, pk):
    if request.is_ajax():
        result = get_object_or_404(Product, pk=pk).price
        return JsonResponse({
            'result': result
        })
