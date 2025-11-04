"""
自定义分页类
"""
from rest_framework.pagination import PageNumberPagination
from .response import APIResponse


class CustomPagination(PageNumberPagination):
    """
    自定义分页类
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        返回标准化的分页响应
        """
        return APIResponse(
            code=200,
            msg='success',
            data={
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data,
                'page': self.page.number,
                'page_size': self.page_size,
                'total_pages': self.page.paginator.num_pages,
            }
        )

