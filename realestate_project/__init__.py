# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

# 使用 PyMySQL 替代 mysqlclient
import pymysql
pymysql.install_as_MySQLdb()

__all__ = ('celery_app',)

