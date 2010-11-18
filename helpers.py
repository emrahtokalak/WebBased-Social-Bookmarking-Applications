# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage

import datetime


class EasyPagination(object):

    def __init__(self, request, target_object, limit_per_page):
        self.request        = request
        self.target_object  = target_object
        self.limit_per_page = limit_per_page

    def paginate(self):
        paginator = Paginator(self.target_object, self.limit_per_page) # 

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            items  = paginator.page(page)
        except (EmptyPage, InvalidPage):
            items  = paginator.page(paginator.num_pages)

        return items


