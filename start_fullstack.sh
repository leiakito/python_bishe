#!/bin/bash

# 全栈启动脚本 - 同时启动前后端

echo "========================================="
echo "  二手房可视化系统 - 全栈启动脚本"
echo "========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未检测到Python3"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未检测到Node.js"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"
echo "✅ Node.js版本: $(node -v)"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: 未找到Python虚拟环境"
    echo "   请先运行: python3 -m venv venv"
    exit 1
fi

# 检查前端依赖
if [ ! -d "front/node_modules" ]; then
    echo "📦 正在安装前端依赖..."
    cd front
    npm install
    cd ..
    echo ""
fi

echo "🚀 正在启动服务..."
echo ""

# 激活虚拟环境
source venv/bin/activate

# 加载数据fixtures（如果存在）
if [ -d "data_fixtures" ] && [ "$(ls -A data_fixtures/*.json 2>/dev/null)" ]; then
    echo "📦 检测到数据文件，正在加载..."
    python manage.py load_fixtures > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ 数据加载成功"
    else
        echo "⚠️  数据加载失败（可能已存在数据）"
    fi
    echo ""
fi

# 启动后端（后台运行）
echo "📡 启动Django后端服务 (端口8000)..."
python manage.py runserver > logs/django.log 2>&1 &
DJANGO_PID=$!
echo "   后端PID: $DJANGO_PID"

# 等待后端启动
sleep 3

# 启动Celery Worker（后台运行）
echo "⚙️  启动Celery Worker..."
celery -A realestate_project worker -l info > logs/celery_worker.log 2>&1 &
CELERY_WORKER_PID=$!
echo "   Celery Worker PID: $CELERY_WORKER_PID"

# 启动Celery Beat（后台运行）
echo "⏰ 启动Celery Beat..."
celery -A realestate_project beat -l info > logs/celery_beat.log 2>&1 &
CELERY_BEAT_PID=$!
echo "   Celery Beat PID: $CELERY_BEAT_PID"

# 等待所有后端服务启动
sleep 2

# 启动前端（前台运行）
echo "🎨 启动Vue前端服务 (端口3000)..."
echo ""
echo "========================================="
echo "  所有服务已启动"
echo "========================================="
echo ""
echo "📡 后端API: http://localhost:8000"
echo "🎨 前端界面: http://localhost:3000"
echo "📊 Django Admin: http://localhost:8000/admin"
echo ""
echo "📝 日志文件:"
echo "   - Django: logs/django.log"
echo "   - Celery Worker: logs/celery_worker.log"
echo "   - Celery Beat: logs/celery_beat.log"
echo ""
echo "⚠️  按 Ctrl+C 停止所有服务"
echo "========================================="
echo ""

cd front
npm run dev

# 捕获退出信号，清理后台进程
trap "echo ''; echo '🛑 正在停止所有服务...'; kill $DJANGO_PID $CELERY_WORKER_PID $CELERY_BEAT_PID 2>/dev/null; echo '✅ 所有服务已停止'; exit" INT TERM

