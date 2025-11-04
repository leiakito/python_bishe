#!/bin/bash
# 二手房可视化系统 - 一键初始化脚本

echo "=========================================="
echo "  二手房可视化系统 - 一键初始化"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在虚拟环境中
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}警告: 未检测到虚拟环境${NC}"
    echo "建议先激活虚拟环境: source venv/bin/activate"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 步骤1: 检查MySQL连接
echo -e "${YELLOW}[1/7] 检查MySQL连接...${NC}"
read -p "请输入MySQL root密码: " -s MYSQL_PASSWORD
echo ""

# 测试MySQL连接
if mysql -u root -p"$MYSQL_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MySQL连接成功${NC}"
else
    echo -e "${RED}✗ MySQL连接失败，请检查密码${NC}"
    exit 1
fi

# 步骤2: 创建/重建数据库
echo -e "${YELLOW}[2/7] 创建数据库...${NC}"
mysql -u root -p"$MYSQL_PASSWORD" <<EOF
DROP DATABASE IF EXISTS realestate_db;
CREATE DATABASE realestate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据库创建成功${NC}"
else
    echo -e "${RED}✗ 数据库创建失败${NC}"
    exit 1
fi

# 步骤3: 更新settings.py中的密码
echo -e "${YELLOW}[3/7] 配置数据库密码...${NC}"
sed -i.bak "s/'PASSWORD': '[^']*'/'PASSWORD': '$MYSQL_PASSWORD'/" realestate_project/settings.py
echo -e "${GREEN}✓ 密码配置完成${NC}"

# 步骤4: 生成迁移文件
echo -e "${YELLOW}[4/7] 生成数据库迁移文件...${NC}"
python manage.py makemigrations users
python manage.py makemigrations houses
python manage.py makemigrations favorites
python manage.py makemigrations analysis
echo -e "${GREEN}✓ 迁移文件生成完成${NC}"

# 步骤5: 执行数据库迁移（创建表结构）
echo -e "${YELLOW}[5/7] 创建数据库表结构...${NC}"
python manage.py migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据库表创建成功${NC}"
else
    echo -e "${RED}✗ 数据库迁移失败${NC}"
    exit 1
fi

# 步骤6: 创建超级管理员
echo -e "${YELLOW}[6/7] 创建超级管理员账号...${NC}"
echo "请输入管理员信息（或直接回车使用默认值）:"
read -p "用户名 [admin]: " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-admin}
read -p "邮箱 [admin@example.com]: " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}
read -p "密码 [admin123]: " -s ADMIN_PASSWORD
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
echo ""

# 使用Python脚本创建超级用户
python manage.py shell <<EOF
from apps.users.models import User
if not User.objects.filter(username='$ADMIN_USER').exists():
    User.objects.create_superuser('$ADMIN_USER', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')
    print('超级管理员创建成功')
else:
    print('超级管理员已存在')
EOF

echo -e "${GREEN}✓ 超级管理员配置完成${NC}"

# 步骤7: 初始化测试数据
echo -e "${YELLOW}[7/7] 初始化测试数据...${NC}"
read -p "是否初始化测试数据（包含50个房源、8个区域）? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py shell < scripts/init_data.py
    echo -e "${GREEN}✓ 测试数据初始化完成${NC}"
else
    echo -e "${YELLOW}跳过测试数据初始化${NC}"
fi

# 完成
echo ""
echo "=========================================="
echo -e "${GREEN}  ✓ 初始化完成！${NC}"
echo "=========================================="
echo ""
echo "📊 数据库信息:"
echo "  - 数据库名: realestate_db"
echo "  - 用户名: root"
echo "  - 密码: $MYSQL_PASSWORD"
echo ""
echo "👤 管理员账号:"
echo "  - 用户名: $ADMIN_USER"
echo "  - 密码: $ADMIN_PASSWORD"
echo "  - 邮箱: $ADMIN_EMAIL"
echo ""
echo "🚀 启动服务:"
echo "  python manage.py runserver"
echo ""
echo "🌐 访问地址:"
echo "  - API接口: http://localhost:8000/api/"
echo "  - 管理后台: http://localhost:8000/admin/"
echo ""
echo "📖 查看文档:"
echo "  - API文档: API_DOCUMENTATION.md"
echo "  - 快速指南: QUICKSTART.md"
echo ""

