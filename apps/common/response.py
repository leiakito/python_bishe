"""
统一的API响应格式
"""
from rest_framework.response import Response
from rest_framework import status


class APIResponse(Response):
    """
    标准化的API响应类
    格式: {"code": 200, "msg": "success", "data": {...}}
    """
    def __init__(self, code=200, msg='success', data=None, status_code=None, **kwargs):
        response_data = {
            'code': code,
            'msg': msg,
            'data': data if data is not None else {}
        }
        
        # 如果没有指定HTTP状态码,根据code自动设置
        if status_code is None:
            if 200 <= code < 300:
                status_code = status.HTTP_200_OK
            elif 400 <= code < 500:
                status_code = status.HTTP_400_BAD_REQUEST
            elif 500 <= code < 600:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            else:
                status_code = status.HTTP_200_OK
        
        super().__init__(data=response_data, status=status_code, **kwargs)


def success_response(data=None, msg='success', code=200):
    """成功响应"""
    return APIResponse(code=code, msg=msg, data=data)


def error_response(msg='error', code=400, data=None):
    """错误响应"""
    return APIResponse(code=code, msg=msg, data=data)

