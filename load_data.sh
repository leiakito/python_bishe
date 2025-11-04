#!/bin/bash
# 数据加载快捷脚本

echo "========================================"
echo "  数据加载工具"
echo "========================================"
echo ""

# 激活虚拟环境
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "❌ 错误: 找不到虚拟环境"
        exit 1
    fi
fi

# 检查data_fixtures文件夹
if [ ! -d "data_fixtures" ]; then
    echo "❌ 错误: 找不到 data_fixtures 文件夹"
    exit 1
fi

# 统计JSON文件数量
json_count=$(find data_fixtures -name "*.json" -not -name "template.json" | wc -l | tr -d ' ')

if [ "$json_count" -eq 0 ]; then
    echo "⚠️  data_fixtures 文件夹中没有JSON数据文件"
    echo ""
    echo "使用方法:"
    echo "1. 复制模板文件: cp data_fixtures/template.json data_fixtures/my_data.json"
    echo "2. 编辑文件内容"
    echo "3. 重新运行此脚本"
    exit 0
fi

echo "📁 找到 $json_count 个数据文件"
echo ""

# 显示菜单
echo "请选择操作:"
echo "  1) 导入数据（保留现有数据）"
echo "  2) 清除并导入（删除所有现有数据）"
echo "  3) 仅查看数据统计"
echo "  4) 退出"
echo ""
read -p "请输入选项 [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 开始导入数据..."
        python manage.py load_fixtures
        ;;
    2)
        echo ""
        read -p "⚠️  确定要删除所有现有数据吗? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo ""
            echo "🚀 清除现有数据并导入..."
            python manage.py load_fixtures --clear
        else
            echo "❌ 操作已取消"
            exit 0
        fi
        ;;
    3)
        echo ""
        echo "📊 当前数据统计:"
        python manage.py shell -c "
from apps.houses.models import House, Transaction
from apps.houses.models import District

print(f'房源总数: {House.objects.count()}')
print(f'成交记录总数: {Transaction.objects.count()}')
print('')
print('各区域房源统计:')
for district in District.objects.all():
    count = House.objects.filter(district=district).count()
    if count > 0:
        print(f'  {district.name}: {count}套')
"
        ;;
    4)
        echo "👋 再见!"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "✅ 完成!"

