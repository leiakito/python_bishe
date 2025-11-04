#!/bin/bash
# 二手房可视化系统 - 启动所有服务（Django + Celery + Redis）

echo "=========================================="
echo "  二手房可视化系统 - 启动所有服务"
echo "=========================================="
echo ""

# 检查虚拟环境
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查 Redis 是否运行
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis 未运行，尝试启动..."
    if command -v redis-server &> /dev/null; then
        redis-server --daemonize yes
        echo "✓ Redis 已启动"
    else
        echo "❌ Redis 未安装，Celery 功能将不可用"
        echo "安装 Redis: brew install redis"
    fi
fi

echo ""
echo "启动服务（使用 tmux 或 screen 管理多个进程）..."
echo ""
echo "如果您安装了 tmux，可以使用以下命令："
echo "  tmux new-session -d -s django 'python manage.py runserver'"
echo "  tmux new-session -d -s celery 'celery -A realestate_project worker -l info'"
echo "  tmux new-session -d -s beat 'celery -A realestate_project beat -l info'"
echo ""
echo "或者手动在不同终端中运行："
echo "  终端1: python manage.py runserver"
echo "  终端2: celery -A realestate_project worker -l info"
echo "  终端3: celery -A realestate_project beat -l info"
echo ""

# 只启动 Django（推荐新手）
echo "现在启动 Django 服务器..."
python manage.py runserver

