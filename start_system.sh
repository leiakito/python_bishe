#!/bin/bash
# 二手房可视化系统 - 一键启动脚本
# 整合所有功能：初始化、数据迁移、启动服务

set -e  # 遇到错误立即退出

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==================== 日志函数 ====================
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

log_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

# ==================== 显示欢迎信息 ====================
show_banner() {
    clear
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║          二手房可视化系统 - 一键启动脚本 v2.0              ║"
    echo "║                                                              ║"
    echo "║  功能: 智能检测 + 自动初始化 + 数据迁移 + 全栈启动        ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# ==================== 状态文件管理 ====================
STATUS_FILE=".system_status"

# 初始化状态文件
init_status_file() {
    if [ ! -f "$STATUS_FILE" ]; then
        cat > "$STATUS_FILE" <<EOF
dependencies_checked=false
venv_created=false
python_deps_installed=false
frontend_deps_installed=false
database_created=false
migrations_applied=false
superuser_created=false
sample_users_created=false
data_loaded=false
EOF
    fi
}

# 读取状态
get_status() {
    local key=$1
    if [ -f "$STATUS_FILE" ]; then
        grep "^${key}=" "$STATUS_FILE" | cut -d'=' -f2
    else
        echo "false"
    fi
}

# 设置状态
set_status() {
    local key=$1
    local value=$2
    if [ -f "$STATUS_FILE" ]; then
        sed -i.bak "s/^${key}=.*/${key}=${value}/" "$STATUS_FILE"
        rm -f "${STATUS_FILE}.bak"
    fi
}

# 重置所有状态（用于重新初始化）
reset_all_status() {
    rm -f "$STATUS_FILE"
    init_status_file
}

# ==================== 检查系统依赖 ====================
check_dependencies() {
    if [ "$(get_status dependencies_checked)" = "true" ]; then
        log_success "系统依赖已检查"
        return 0
    fi
    
    log_step "检查系统依赖..."
    
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
    
    set_status "dependencies_checked" "true"
    echo ""
}

# ==================== 创建必要的目录 ====================
create_directories() {
    log_step "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p media/houses/images
    mkdir -p static
    mkdir -p data_fixtures
    
    log_success "目录创建完成"
    echo ""
}

# ==================== 设置Python虚拟环境 ====================
setup_venv() {
    log_step "设置Python虚拟环境..."
    
    if [ "$(get_status venv_created)" = "true" ] && [ -d "venv" ]; then
        log_success "虚拟环境已存在"
    else
        log_info "创建虚拟环境..."
        python3 -m venv venv
        set_status "venv_created" "true"
        log_success "虚拟环境创建成功"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    log_success "虚拟环境已激活"
    
    # 安装/更新Python依赖
    if [ "$(get_status python_deps_installed)" = "false" ]; then
        log_info "升级pip..."
        pip install --upgrade pip > /dev/null 2>&1
        
        log_info "安装Python依赖包（这可能需要几分钟）..."
        pip install -r requirements.txt > /dev/null 2>&1
        set_status "python_deps_installed" "true"
        log_success "Python依赖安装完成"
    else
        log_success "Python依赖已安装"
    fi
    
    echo ""
}

# ==================== 配置数据库 ====================
setup_database() {
    if [ "$(get_status database_created)" = "true" ]; then
        log_success "数据库已配置"
        return 0
    fi
    
    log_step "配置MySQL数据库..."
    
    # 获取MySQL密码
    read -p "请输入MySQL root密码: " -s MYSQL_PASSWORD
    echo ""
    
    # 测试连接
    if ! mysql -u root -p"$MYSQL_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; then
        log_error "MySQL连接失败，请检查密码"
        exit 1
    fi
    log_success "MySQL连接成功"
    
    # 检查数据库是否存在
    if mysql -u root -p"$MYSQL_PASSWORD" -e "USE realestate_db" > /dev/null 2>&1; then
        log_success "数据库已存在"
    else
        log_info "创建新数据库..."
        mysql -u root -p"$MYSQL_PASSWORD" <<EOF
CREATE DATABASE realestate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
        log_success "数据库创建成功"
    fi
    
    # 更新settings.py中的数据库密码
    log_info "配置数据库连接..."
    if [ -f "realestate_project/settings.py" ]; then
        cp realestate_project/settings.py realestate_project/settings.py.bak 2>/dev/null || true
        sed -i.tmp "s/'PASSWORD': '[^']*'/'PASSWORD': '$MYSQL_PASSWORD'/" realestate_project/settings.py
        rm -f realestate_project/settings.py.tmp 2>/dev/null || true
        log_success "数据库配置完成"
    fi
    
    set_status "database_created" "true"
    echo ""
}

# ==================== 数据库迁移（只执行一次） ====================
migrate_database() {
    if [ "$(get_status migrations_applied)" = "true" ]; then
        log_success "数据库迁移已完成（跳过）"
        return 0
    fi
    
    log_step "执行数据库迁移（首次运行）..."
    
    # 生成迁移文件
    log_info "生成迁移文件..."
    python manage.py makemigrations 2>&1 | grep -v "No changes detected" || true
    
    # 执行迁移
    log_info "应用数据库迁移..."
    python manage.py migrate
    
    set_status "migrations_applied" "true"
    log_success "数据库迁移完成"
    echo ""
}

# ==================== 创建超级用户 ====================
create_superuser() {
    if [ "$(get_status superuser_created)" = "true" ]; then
        log_success "管理员账号已创建"
        return 0
    fi
    
    log_step "配置管理员账号..."
    
    # 检查是否已有超级用户
    has_superuser=$(python manage.py shell -c "from apps.users.models import User; print('yes' if User.objects.filter(is_superuser=True).exists() else 'no')" 2>/dev/null || echo "no")
    
    if [ "$has_superuser" = "yes" ]; then
        log_success "检测到已有管理员账号"
        set_status "superuser_created" "true"
        echo ""
        return 0
    fi
    
    echo ""
    log_info "请输入管理员信息（或直接回车使用默认值）"
    read -p "用户名 [admin]: " ADMIN_USER
    ADMIN_USER=${ADMIN_USER:-admin}
    
    read -p "邮箱 [admin@example.com]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}
    
    read -p "手机号 [13800000000]: " ADMIN_PHONE
    ADMIN_PHONE=${ADMIN_PHONE:-13800000000}
    
    read -p "密码 [admin123]: " -s ADMIN_PASSWORD
    ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
    echo ""
    
    # 创建超级用户
    python manage.py shell <<EOF
from apps.users.models import User
if not User.objects.filter(username='$ADMIN_USER').exists():
    User.objects.create_superuser(
        username='$ADMIN_USER',
        email='$ADMIN_EMAIL',
        password='$ADMIN_PASSWORD',
        phone='$ADMIN_PHONE',
        role='admin'
    )
    print('✓ 管理员创建成功')
else:
    print('! 管理员用户名已存在')
EOF
    
    # 保存管理员信息供后续使用
    SAVED_ADMIN_USER=$ADMIN_USER
    SAVED_ADMIN_PASSWORD=$ADMIN_PASSWORD
    
    set_status "superuser_created" "true"
    echo ""
}

# ==================== 创建示例用户 ====================
create_sample_users() {
    if [ "$(get_status sample_users_created)" = "true" ]; then
        log_success "示例用户已创建"
        return 0
    fi
    
    log_step "创建示例用户..."
    
    python manage.py shell <<EOF
from apps.users.models import User

# 创建经纪人账户
if not User.objects.filter(username='agent1').exists():
    User.objects.create_user(
        username='agent1',
        email='agent1@example.com',
        password='agent123',
        phone='13800138001',
        real_name='张红',
        role='agent'
    )
    print('✓ 经纪人账户 agent1 创建成功')

# 创建普通用户
if not User.objects.filter(username='user1').exists():
    User.objects.create_user(
        username='user1',
        email='user1@example.com',
        password='user123',
        phone='13800138002',
        real_name='李明',
        role='user'
    )
    print('✓ 普通用户 user1 创建成功')
EOF
    
    set_status "sample_users_created" "true"
    echo ""
}

# ==================== 加载示例数据 ====================
load_sample_data() {
    if [ "$(get_status data_loaded)" = "true" ]; then
        log_success "数据已加载"
        return 0
    fi
    
    log_step "检查示例数据..."
    
    # 检查是否有数据文件
    if [ -d "data_fixtures" ] && [ "$(ls -A data_fixtures/*.json 2>/dev/null)" ]; then
        json_count=$(find data_fixtures -name "*.json" -not -name "template.json" 2>/dev/null | wc -l | tr -d ' ')
        
        if [ "$json_count" -gt 0 ]; then
            log_info "找到 $json_count 个数据文件"
            echo ""
            read -p "是否加载数据文件? (y/n) [y]: " load_data
            load_data=${load_data:-y}
            
            if [[ $load_data =~ ^[Yy]$ ]]; then
                python manage.py load_fixtures
                set_status "data_loaded" "true"
                log_success "数据加载完成"
            else
                log_info "跳过数据加载"
            fi
        fi
    else
        log_warning "未找到数据文件，跳过数据加载"
        log_info "提示: 您可以将JSON数据文件放在 data_fixtures/ 目录下"
    fi
    
    echo ""
}

# ==================== 安装前端依赖 ====================
setup_frontend() {
    if [ "$(get_status frontend_deps_installed)" = "true" ] && [ -d "front/node_modules" ]; then
        log_success "前端依赖已安装"
        return 0
    fi
    
    log_step "配置前端项目..."
    
    if [ ! -d "front" ]; then
        log_error "未找到前端目录"
        return
    fi
    
    cd front
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖包（这可能需要几分钟）..."
        npm install
        set_status "frontend_deps_installed" "true"
        log_success "前端依赖安装完成"
    else
        log_success "前端依赖已安装"
    fi
    
    cd ..
    echo ""
}

# ==================== 启动Redis ====================
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

# ==================== 启动所有服务 ====================
start_services() {
    log_step "准备启动服务..."
    echo ""
    
    # 确保虚拟环境已激活
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source venv/bin/activate
    fi
    
    # 启动Redis
    start_redis
    
    echo "══════════════════════════════════════════════════════════════"
    echo "  🚀 正在启动所有服务..."
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    
    # 确保日志目录存在
    mkdir -p logs
    
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
    echo "══════════════════════════════════════════════════════════════"
    echo "  ✅ 后端服务已启动"
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    echo "📡 后端服务:"
    echo "   - API接口: http://localhost:8000/api/"
    echo "   - Django Admin: http://localhost:8000/admin/"
    echo "   - API文档: http://localhost:8000/api/docs/"
    echo ""
    echo "👤 测试账号:"
    if [ ! -z "$SAVED_ADMIN_USER" ]; then
        echo "   管理员: $SAVED_ADMIN_USER / $SAVED_ADMIN_PASSWORD"
    else
        echo "   管理员: admin / admin123"
    fi
    echo "   经纪人: agent1 / agent123"
    echo "   普通用户: user1 / user123"
    echo ""
    echo "📝 日志文件:"
    echo "   - Django: logs/django.log"
    if [ ! -z "$CELERY_WORKER_PID" ]; then
        echo "   - Celery Worker: logs/celery_worker.log"
        echo "   - Celery Beat: logs/celery_beat.log"
    fi
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    
    # 启动前端（前台运行）
    log_info "启动Vue前端服务 (端口3000)..."
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  🎨 正在启动前端服务..."
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    echo "🌐 前端访问地址: http://localhost:3000"
    echo ""
    echo "⚠️  按 Ctrl+C 停止所有服务"
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    
    cd front
    npm run dev
    
    # 这行代码在Ctrl+C后执行
    cd ..
}

# ==================== 清理函数 ====================
cleanup() {
    echo ""
    log_warning "正在停止所有服务..."
    
    # 从文件读取PID并终止
    if [ -f ".pids" ]; then
        while read pid; do
            if kill -0 $pid 2>/dev/null; then
                kill $pid 2>/dev/null || true
            fi
        done < .pids
        rm -f .pids
    fi
    
    log_success "所有服务已停止"
    exit 0
}

# 注册清理函数
trap cleanup INT TERM

# ==================== 显示系统状态 ====================
show_status() {
    echo "══════════════════════════════════════════════════════════════"
    echo "  系统状态"
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    
    local status_items=(
        "dependencies_checked:系统依赖检查"
        "venv_created:虚拟环境创建"
        "python_deps_installed:Python依赖安装"
        "frontend_deps_installed:前端依赖安装"
        "database_created:数据库创建"
        "migrations_applied:数据库迁移"
        "superuser_created:管理员账号创建"
        "sample_users_created:示例用户创建"
        "data_loaded:示例数据加载"
    )
    
    for item in "${status_items[@]}"; do
        local key="${item%%:*}"
        local desc="${item##*:}"
        local status=$(get_status "$key")
        
        if [ "$status" = "true" ]; then
            echo -e "  ${GREEN}✓${NC} $desc"
        else
            echo -e "  ${YELLOW}○${NC} $desc"
        fi
    done
    
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo ""
}

# ==================== 主函数 ====================
main() {
    show_banner
    
    # 初始化状态文件
    init_status_file
    
    # 询问执行模式
    echo "请选择执行模式:"
    echo ""
    echo "  1) 完整初始化（首次使用）"
    echo "     - 检查依赖、创建环境、配置数据库、迁移数据、启动服务"
    echo ""
    echo "  2) 快速启动（已完成初始化）"
    echo "     - 直接启动前后端服务，跳过所有初始化步骤"
    echo ""
    echo "  3) 增量初始化（补充缺失步骤）"
    echo "     - 智能检测并只执行未完成的初始化步骤"
    echo ""
    echo "  4) 重新初始化（重置所有状态）"
    echo "     - 清除状态记录，重新执行完整初始化"
    echo ""
    echo "  5) 查看系统状态"
    echo "     - 显示当前初始化完成情况"
    echo ""
    echo "  6) 退出"
    echo ""
    read -p "请选择 [1-6]: " mode
    echo ""
    
    case $mode in
        1)
            # 完整初始化流程
            log_info "开始完整初始化..."
            echo ""
            
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
                echo "  ./start_system.sh"
                echo "  然后选择模式 2 (快速启动)"
            fi
            ;;
            
        2)
            # 快速启动模式
            log_info "快速启动模式..."
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
            # 增量初始化模式
            log_info "增量初始化模式（智能检测未完成步骤）..."
            echo ""
            
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
            log_success "增量初始化完成！"
            echo ""
            read -p "是否立即启动服务? (y/n) [y]: " start_now
            start_now=${start_now:-y}
            
            if [[ $start_now =~ ^[Yy]$ ]]; then
                start_services
            fi
            ;;
            
        4)
            # 重新初始化
            log_warning "重新初始化模式..."
            echo ""
            read -p "⚠️  确定要清除所有状态并重新初始化吗? (yes/no): " confirm
            
            if [ "$confirm" = "yes" ]; then
                reset_all_status
                log_success "状态已重置"
                echo ""
                log_info "请重新运行脚本并选择模式1（完整初始化）"
            else
                log_info "操作已取消"
            fi
            ;;
            
        5)
            # 查看系统状态
            show_status
            echo ""
            read -p "按回车键返回..." dummy
            main
            ;;
            
        6)
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
