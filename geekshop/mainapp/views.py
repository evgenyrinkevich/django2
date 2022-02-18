from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

import json
import os

from django.views.generic import DetailView, TemplateView, ListView
from django.conf import settings
from django.core.cache import cache

from mainapp.mixin import BaseClassContextMixin
from mainapp.models import Product, ProductCategory

MODULE_DIR = os.path.dirname(__file__)


class IndexTemplateView(TemplateView, BaseClassContextMixin):
    template_name = 'mainapp/index.html'
    title = 'Geekshop'


def get_link_category():
    if settings.LOW_CACHE:
        key = 'link_category'
        link_category = cache.get(key)
        if link_category is None:
            link_category = ProductCategory.objects.filter(is_active=True)
            cache.set(key, link_category)
        return link_category
    else:
        return ProductCategory.objects.filter(is_active=True)


def get_products(id_category):
    if settings.LOW_CACHE:
        key = f'category_{id_category}'
        link_product = cache.get(key)
        if link_product is None:
            if id_category:
                link_product = Product.objects.filter(category_id=id_category, is_active=True).select_related(
                    'category')
            else:
                link_product = Product.objects.filter(is_active=True).select_related('category')
            cache.set(key, link_product)
        return link_product
    else:
        if id_category:
            return Product.objects.filter(category_id=id_category, is_active=True).select_related('category')
        else:
            return Product.objects.all().select_related('category')


def get_product(pk):
    if settings.LOW_CACHE:
        key = f'product_{pk}'
        product = cache.get(key)
        if product is None:
            product = Product.objects.get(id=pk)
            cache.set(key, product)
        return product
    else:
        return Product.objects.get(id=pk)


def products(request, id_category=None, page=1):
    context = {
        'title': 'Geekshop | Каталог',
    }

    products_list = get_products(id_category).order_by('name')
    paginator = Paginator(products_list, per_page=3)

    try:
        products_paginator = paginator.page(page)
    except PageNotAnInteger:
        products_paginator = paginator.page(1)
    except EmptyPage:
        products_paginator = paginator.page(paginator.num_pages)

    context['products'] = products_paginator
    context['categories'] = get_link_category()
    return render(request, 'mainapp/products.html', context)


class ProductDetail(DetailView):
    """
    Контроллер вывода информации о продукте
    """
    model = Product
    template_name = 'mainapp/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        # product = self.get_object()
        context['product'] = get_product(self.kwargs.get('pk'))
        return context
