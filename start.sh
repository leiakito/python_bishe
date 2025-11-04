#!/bin/bash
# 二手房可视化系统 - 快速启动脚本

echo "=========================================="
echo "  二手房可视化系统 - 启动服务"
echo "=========================================="
echo ""

# 检查虚拟环境
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查数据库是否已初始化
if ! python manage.py showmigrations | grep -q "\[X\]"; then
    echo "⚠️  检测到数据库未初始化"
    echo "请先运行: ./setup.sh"
    exit 1
fi

# 加载数据fixtures（如果存在）
if [ -d "data_fixtures" ] && [ "$(ls -A data_fixtures/*.json 2>/dev/null)" ]; then
    echo "📦 检测到数据文件，正在加载..."
    python manage.py load_fixtures
    echo ""
fi

echo "🚀 启动 Django 开发服务器..."
echo ""
echo "访问地址:"
echo "  - API接口: http://localhost:8000/api/"
echo "  - 管理后台: http://localhost:8000/admin/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python manage.py runserver

