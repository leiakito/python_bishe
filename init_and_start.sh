#!/bin/bash
# 二手房可视化系统 - 完整初始化和启动脚本
# 包含：数据库构建、环境配置、数据加载、前后端启动

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 显示欢迎信息
show_banner() {
    clear
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║        二手房可视化系统 - 完整初始化启动脚本              ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# 检查系统依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "未检测到Python3，请先安装"
        exit 1
    fi
    log_success "Python版本: $(python3 --version)"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "未检测到Node.js，请先安装"
        exit 1
    fi
    log_success "Node.js版本: $(node -v)"
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "未检测到npm，请先安装"
        exit 1
    fi
    log_success "npm版本: $(npm -v)"
    
    # 检查MySQL
    if ! command -v mysql &> /dev/null; then
        log_error "未检测到MySQL，请先安装"
        exit 1
    fi
    log_success "MySQL已安装"
    
    # 检查Redis（可选）
    if command -v redis-cli &> /dev/null; then
        log_success "Redis已安装"
    else
        log_warning "Redis未安装，Celery功能将不可用"
    fi
    
    echo ""
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p media/houses/images
    mkdir -p static
    mkdir -p data_fixtures
    
    log_success "目录创建完成"
    echo ""
}

# 设置Python虚拟环境
setup_venv() {
    log_info "设置Python虚拟环境..."
    
    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境..."
        python3 -m venv venv
        log_success "虚拟环境创建成功"
    else
        log_success "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    log_success "虚拟环境已激活"
    
    # 升级pip
    log_info "升级pip..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # 安装Python依赖
    log_info "安装Python依赖包..."
    pip install -r requirements.txt > /dev/null 2>&1
    log_success "Python依赖安装完成"
    
    echo ""
}

# 配置数据库
setup_database() {
    log_info "配置MySQL数据库..."
    
    # 获取MySQL密码
    read -p "请输入MySQL root密码: " -s MYSQL_PASSWORD
    echo ""
    
    # 测试连接
    if ! mysql -u root -p"$MYSQL_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; then
        log_error "MySQL连接失败，请检查密码"
        exit 1
    fi
    log_success "MySQL连接成功"
    
    # 询问是否重建数据库
    echo ""
    read -p "是否重建数据库（会删除现有数据）? (y/n) [n]: " rebuild_db
    rebuild_db=${rebuild_db:-n}
    
    if [[ $rebuild_db =~ ^[Yy]$ ]]; then
        log_warning "正在删除并重建数据库..."
        mysql -u root -p"$MYSQL_PASSWORD" <<EOF
DROP DATABASE IF EXISTS realestate_db;
CREATE DATABASE realestate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
        log_success "数据库重建成功"
    else
        # 检查数据库是否存在
        if ! mysql -u root -p"$MYSQL_PASSWORD" -e "USE realestate_db" > /dev/null 2>&1; then
            log_info "创建新数据库..."
            mysql -u root -p"$MYSQL_PASSWORD" <<EOF
CREATE DATABASE realestate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
            log_success "数据库创建成功"
        else
            log_success "数据库已存在"
        fi
    fi
    
    # 更新settings.py中的数据库密码
    log_info "配置数据库连接..."
    if [ -f "realestate_project/settings.py" ]; then
        # 创建备份
        cp realestate_project/settings.py realestate_project/settings.py.bak
        # 更新密码
        sed -i.tmp "s/'PASSWORD': '[^']*'/'PASSWORD': '$MYSQL_PASSWORD'/" realestate_project/settings.py
        rm realestate_project/settings.py.tmp 2>/dev/null || true
        log_success "数据库配置完成"
    fi
    
    echo ""
}

# 数据库迁移
migrate_database() {
    log_info "执行数据库迁移..."
    
    # 生成迁移文件
    log_info "生成迁移文件..."
    python manage.py makemigrations > /dev/null 2>&1 || true
    
    # 执行迁移
    log_info "应用迁移..."
    python manage.py migrate
    
    log_success "数据库迁移完成"
    echo ""
}

# 创建超级用户
create_superuser() {
    log_info "配置管理员账号..."
    
    # 检查是否已有超级用户
    has_superuser=$(python manage.py shell -c "from apps.users.models import User; print('yes' if User.objects.filter(is_superuser=True).exists() else 'no')")
    
    if [ "$has_superuser" = "yes" ]; then
        log_success "管理员账号已存在"
        echo ""
        read -p "是否创建新的管理员账号? (y/n) [n]: " create_new
        create_new=${create_new:-n}
        if [[ ! $create_new =~ ^[Yy]$ ]]; then
            echo ""
            return
        fi
    fi
    
    echo ""
    log_info "请输入管理员信息（或直接回车使用默认值）"
    read -p "用户名 [admin]: " ADMIN_USER
    ADMIN_USER=${ADMIN_USER:-admin}
    
    read -p "邮箱 [admin@example.com]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}
    
    read -p "密码 [admin123]: " -s ADMIN_PASSWORD
    ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
    echo ""
    
    # 创建超级用户
    python manage.py shell <<EOF
from apps.users.models import User
if not User.objects.filter(username='$ADMIN_USER').exists():
    User.objects.create_superuser('$ADMIN_USER', '$ADMIN_EMAIL', '$ADMIN_PASSWORD', role='admin')
    print('✓ 管理员创建成功')
else:
    print('! 管理员用户名已存在')
EOF
    
    # 保存管理员信息供后续使用
    SAVED_ADMIN_USER=$ADMIN_USER
    SAVED_ADMIN_PASSWORD=$ADMIN_PASSWORD
    
    echo ""
}

# 创建示例用户
create_sample_users() {
    log_info "创建示例用户..."
    
    python manage.py shell <<EOF
from apps.users.models import User

# 创建经纪人账户
if not User.objects.filter(username='agent1').exists():
    User.objects.create_user(
        username='agent1',
        email='agent1@example.com',
        password='agent123',
        real_name='张红',
        role='agent',
        phone='13800138001'
    )
    print('✓ 经纪人账户 agent1 创建成功')

# 创建普通用户
if not User.objects.filter(username='user1').exists():
    User.objects.create_user(
        username='user1',
        email='user1@example.com',
        password='user123',
        real_name='李明',
        role='user',
        phone='13800138002'
    )
    print('✓ 普通用户 user1 创建成功')
EOF
    
    echo ""
}

# 加载示例数据
load_sample_data() {
    log_info "加载示例数据..."
    
    # 检查是否有数据文件
    if [ -d "data_fixtures" ] && [ "$(ls -A data_fixtures/*.json 2>/dev/null)" ]; then
        json_count=$(find data_fixtures -name "*.json" -not -name "template.json" | wc -l | tr -d ' ')
        echo ""
        log_info "找到 $json_count 个数据文件"
        read -p "是否加载数据文件? (y/n) [y]: " load_data
        load_data=${load_data:-y}
        
        if [[ $load_data =~ ^[Yy]$ ]]; then
            python manage.py load_fixtures
            log_success "数据加载完成"
        fi
    else
        log_warning "未找到数据文件，跳过数据加载"
    fi
    
    echo ""
}

# 安装前端依赖
setup_frontend() {
    log_info "配置前端项目..."
    
    if [ ! -d "front" ]; then
        log_error "未找到前端目录"
        return
    fi
    
    cd front
    
    # 检查并安装依赖
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖包（这可能需要几分钟）..."
        npm install
        log_success "前端依赖安装完成"
    else
        log_success "前端依赖已安装"
    fi
    
    cd ..
    echo ""
}

# 启动Redis（如果需要）
start_redis() {
    if command -v redis-cli &> /dev/null; then
        if ! redis-cli ping > /dev/null 2>&1; then
            log_info "启动Redis..."
            if command -v redis-server &> /dev/null; then
                redis-server --daemonize yes
                sleep 1
                if redis-cli ping > /dev/null 2>&1; then
                    log_success "Redis启动成功"
                fi
            fi
        else
            log_success "Redis已在运行"
        fi
    fi
}

# 启动所有服务
start_services() {
    log_info "准备启动服务..."
    echo ""
    
    # 确保虚拟环境已激活
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source venv/bin/activate
    fi
    
    # 启动Redis
    start_redis
    
    echo "════════════════════════════════════════════════════════════"
    echo "  🚀 正在启动所有服务..."
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    # 启动Django后端（后台）
    log_info "启动Django后端服务 (端口8000)..."
    python manage.py runserver 0.0.0.0:8000 > logs/django.log 2>&1 &
    DJANGO_PID=$!
    echo "   PID: $DJANGO_PID"
    
    # 等待后端启动
    sleep 3
    
    # 启动Celery Worker（后台，如果Redis可用）
    if redis-cli ping > /dev/null 2>&1; then
        log_info "启动Celery Worker..."
        celery -A realestate_project worker -l info > logs/celery_worker.log 2>&1 &
        CELERY_WORKER_PID=$!
        echo "   PID: $CELERY_WORKER_PID"
        
        # 启动Celery Beat（后台）
        log_info "启动Celery Beat..."
        celery -A realestate_project beat -l info > logs/celery_beat.log 2>&1 &
        CELERY_BEAT_PID=$!
        echo "   PID: $CELERY_BEAT_PID"
        
        sleep 2
    fi
    
    # 保存PID到文件
    echo $DJANGO_PID > .pids
    [ ! -z "$CELERY_WORKER_PID" ] && echo $CELERY_WORKER_PID >> .pids
    [ ! -z "$CELERY_BEAT_PID" ] && echo $CELERY_BEAT_PID >> .pids
    
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  ✅ 后端服务已启动"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "📡 后端服务:"
    echo "   - API接口: http://localhost:8000/api/"
    echo "   - Django Admin: http://localhost:8000/admin/"
    echo ""
    echo "👤 登录账号:"
    if [ ! -z "$SAVED_ADMIN_USER" ]; then
        echo "   管理员: $SAVED_ADMIN_USER / $SAVED_ADMIN_PASSWORD"
    fi
    echo "   经纪人: agent1 / agent123"
    echo "   普通用户: user1 / user123"
    echo ""
    echo "📝 日志文件:"
    echo "   - Django: logs/django.log"
    echo "   - Celery Worker: logs/celery_worker.log"
    echo "   - Celery Beat: logs/celery_beat.log"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    # 启动前端（前台运行）
    log_info "启动Vue前端服务 (端口3000)..."
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  🎨 正在启动前端服务..."
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "🌐 访问地址: http://localhost:3000"
    echo ""
    echo "⚠️  按 Ctrl+C 停止所有服务"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    cd front
    npm run dev
    
    # 这行代码在Ctrl+C后执行
    cd ..
}

# 清理函数
cleanup() {
    echo ""
    log_warning "正在停止所有服务..."
    
    # 从文件读取PID并终止
    if [ -f ".pids" ]; then
        while read pid; do
            kill $pid 2>/dev/null || true
        done < .pids
        rm .pids
    fi
    
    log_success "所有服务已停止"
    exit 0
}

# 注册清理函数
trap cleanup INT TERM

# 主函数
main() {
    show_banner
    
    # 询问执行模式
    echo "请选择执行模式:"
    echo "  1) 完整初始化（首次使用 - 包含数据库、环境、数据）"
    echo "  2) 仅启动服务（已完成初始化）"
    echo "  3) 重建数据库并启动"
    echo "  4) 退出"
    echo ""
    read -p "请选择 [1-4]: " mode
    
    case $mode in
        1)
            # 完整初始化流程
            check_dependencies
            create_directories
            setup_venv
            setup_database
            migrate_database
            create_superuser
            create_sample_users
            load_sample_data
            setup_frontend
            
            echo ""
            log_success "初始化完成！"
            echo ""
            read -p "是否立即启动服务? (y/n) [y]: " start_now
            start_now=${start_now:-y}
            
            if [[ $start_now =~ ^[Yy]$ ]]; then
                start_services
            else
                echo ""
                log_info "稍后可运行以下命令启动服务:"
                echo "  ./init_and_start.sh"
                echo "  或选择模式 2"
            fi
            ;;
            
        2)
            # 仅启动服务
            log_info "启动服务模式..."
            echo ""
            
            # 检查基本依赖
            if [ ! -d "venv" ]; then
                log_error "未找到虚拟环境，请先运行完整初始化（模式1）"
                exit 1
            fi
            
            if [ ! -d "front/node_modules" ]; then
                log_error "未找到前端依赖，请先运行完整初始化（模式1）"
                exit 1
            fi
            
            start_services
            ;;
            
        3)
            # 重建数据库
            log_warning "重建数据库模式..."
            echo ""
            
            if [ ! -d "venv" ]; then
                log_error "未找到虚拟环境，请先运行完整初始化（模式1）"
                exit 1
            fi
            
            source venv/bin/activate
            setup_database
            migrate_database
            create_superuser
            create_sample_users
            load_sample_data
            
            echo ""
            read -p "是否立即启动服务? (y/n) [y]: " start_now
            start_now=${start_now:-y}
            
            if [[ $start_now =~ ^[Yy]$ ]]; then
                start_services
            fi
            ;;
            
        4)
            log_info "再见！"
            exit 0
            ;;
            
        *)
            log_error "无效选项"
            exit 1
            ;;
    esac
}

# 运行主函数
main

