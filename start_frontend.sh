#!/bin/bash

# 前端启动脚本

echo "========================================="
echo "  二手房可视化系统 - 前端启动脚本"
echo "========================================="
echo ""

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未检测到Node.js，请先安装Node.js"
    echo "   下载地址: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js版本: $(node -v)"
echo "✅ npm版本: $(npm -v)"
echo ""

# 进入前端目录
cd front

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，正在安装依赖..."
    echo "   这可能需要几分钟时间，请耐心等待..."
    echo ""
    npm install
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 依赖安装失败，请检查网络连接"
        echo "   可以尝试使用国内镜像:"
        echo "   npm install --registry=https://registry.npmmirror.com"
        exit 1
    fi
    echo ""
    echo "✅ 依赖安装完成"
    echo ""
fi

echo "🚀 正在启动前端开发服务器..."
echo ""
echo "   访问地址: http://localhost:3000"
echo "   按 Ctrl+C 停止服务"
echo ""
echo "========================================="
echo ""

# 启动开发服务器
npm run dev

