# 数据导入文件夹

这个文件夹用于存放房源和成交记录的 JSON 数据文件。

## 使用方法

### 1. 准备 JSON 数据文件

在此文件夹中创建 JSON 文件，格式如下：

```json
{
  "houses": [
    {
      "title": "浦东新区2室精品房源",
      "district": "浦东新区",
      "address": "浦东新区陆家嘴街道100号某某小区",
      "price": 500.00,
      "unit_price": 50000.00,
      "area": 100.00,
      "house_type": "2室",
      "floor": "10/30",
      "total_floors": 30,
      "orientation": "南",
      "decoration": "精装",
      "build_year": 2020,
      "latitude": 31.2304,
      "longitude": 121.4737,
      "description": "房源描述信息",
      "agent": "agent1",
      "status": "available"
    }
  ],
  "transactions": [
    {
      "house_address": "浦东新区陆家嘴街道100号某某小区",
      "deal_price": 480.00,
      "deal_date": "2025-06-01",
      "buyer_name": "张先生"
    }
  ]
}
```

### 2. 运行导入命令

```bash
# 导入数据（保留现有数据）
python manage.py load_fixtures

# 清除现有数据后导入
python manage.py load_fixtures --clear

# 指定其他文件夹
python manage.py load_fixtures --folder my_data
```

## 字段说明

### houses（房源数据）

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| title | string | 是 | 房源标题 |
| district | string | 是 | 区域名称（如：浦东新区） |
| address | string | 是 | 详细地址（唯一标识） |
| price | number | 是 | 总价（万元） |
| unit_price | number | 是 | 单价（元/㎡） |
| area | number | 是 | 面积（平方米） |
| house_type | string | 是 | 户型（1室/2室/3室/4室/5室及以上） |
| floor | string | 否 | 楼层（如：10/30） |
| total_floors | number | 否 | 总楼层数 |
| orientation | string | 否 | 朝向（南/东/东南/南北） |
| decoration | string | 否 | 装修（精装/简装/毛坯/豪华装修） |
| build_year | number | 否 | 建造年份 |
| latitude | number | 否 | 纬度 |
| longitude | number | 否 | 经度 |
| description | string | 否 | 房源描述 |
| agent | string | 否 | 经纪人用户名（默认：agent1） |
| status | string | 否 | 状态（available/sold/rented，默认：available） |

### transactions（成交记录）

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| house_id | number | * | 房源ID（与house_address二选一） |
| house_address | string | * | 房源地址（与house_id二选一） |
| deal_price | number | 是 | 成交价格（万元） |
| deal_date | string | 是 | 成交日期（YYYY-MM-DD） |
| buyer_name | string | 否 | 买家姓名 |

## 注意事项

1. **数据去重**: 系统会根据 `address` 自动去重，相同地址的房源不会重复导入
2. **成交记录关联**: 成交记录必须关联到已存在的房源（通过 house_id 或 house_address）
3. **区域自动创建**: 如果区域不存在，系统会自动创建
4. **经纪人**: 如果指定的经纪人不存在，会使用第一个可用的经纪人
5. **文件编码**: JSON 文件必须使用 UTF-8 编码
6. **多文件支持**: 可以创建多个 JSON 文件，系统会按顺序加载

## 示例文件

- `example_shanghai.json`: 上海地区示例数据
- `pudong_houses.json`: 浦东新区房源数据
- 可以创建任意命名的 JSON 文件

