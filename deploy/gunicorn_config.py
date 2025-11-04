"""
Gunicorn配置文件
使用方法: gunicorn -c deploy/gunicorn_config.py realestate_project.wsgi:application
"""
import multiprocessing

# 绑定地址
bind = "0.0.0.0:8000"

# Worker进程数
workers = multiprocessing.cpu_count() * 2 + 1

# Worker类型
worker_class = "sync"

# 最大请求数
max_requests = 1000
max_requests_jitter = 50

# 超时时间
timeout = 30
keepalive = 2

# 日志
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "realestate_project"

# Daemon模式
daemon = False

# 预加载应用
preload_app = True

