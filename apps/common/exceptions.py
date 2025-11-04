"""
自定义异常处理
"""
from rest_framework.views import exception_handler
from rest_framework import status
from .response import APIResponse


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    """
    # 调用REST framework默认的异常处理方法
    response = exception_handler(exc, context)
    
    if response is not None:
        # 标准化错误响应格式
        error_msg = '请求失败'
        
        if isinstance(response.data, dict):
            # 提取错误信息
            if 'detail' in response.data:
                error_msg = response.data['detail']
            elif 'error' in response.data:
                error_msg = response.data['error']
            else:
                # 获取第一个错误信息
                for key, value in response.data.items():
                    if isinstance(value, list):
                        error_msg = f"{key}: {value[0]}"
                    else:
                        error_msg = f"{key}: {value}"
                    break
        elif isinstance(response.data, list):
            error_msg = response.data[0] if response.data else '请求失败'
        else:
            error_msg = str(response.data)
        
        return APIResponse(
            code=response.status_code,
            msg=error_msg,
            data=None,
            status_code=response.status_code
        )
    
    # 未被处理的异常
    return APIResponse(
        code=500,
        msg=f'服务器内部错误: {str(exc)}',
        data=None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

