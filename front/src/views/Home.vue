<template>
  <div class="home-page">
    <!-- 轮播图 -->
    <el-carousel height="400px" class="banner">
      <el-carousel-item v-for="item in banners" :key="item.id">
        <div class="banner-item" :style="{ backgroundImage: `url(${item.image})` }">
          <div class="banner-content">
            <h1>{{ item.title }}</h1>
            <p>{{ item.description }}</p>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 搜索栏 -->
    <div class="search-section">
      <el-card>
        <el-form :inline="true" :model="searchForm">
          <el-form-item>
            <el-input
              v-model="searchForm.search"
              placeholder="搜索房源标题、地址"
              style="width: 300px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-select
              v-model="searchForm.district"
              placeholder="选择区域"
              style="width: 150px"
              clearable
            >
              <el-option
                v-for="district in districts"
                :key="district.id"
                :label="district.name"
                :value="district.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-select
              v-model="searchForm.house_type"
              placeholder="户型"
              style="width: 120px"
              clearable
            >
              <el-option label="1室" value="1室" />
              <el-option label="2室" value="2室" />
              <el-option label="3室" value="3室" />
              <el-option label="4室" value="4室" />
              <el-option label="5室及以上" value="5室及以上" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 热门房源 -->
    <div class="hot-houses-section">
      <div class="section-header">
        <h2>热门房源</h2>
        <el-button text type="primary" @click="$router.push('/houses')">
          查看更多 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>

      <el-row :gutter="20" v-loading="loading">
        <el-col
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          v-for="house in hotHouses"
          :key="house.id"
        >
          <el-card
            class="house-card"
            :body-style="{ padding: '0' }"
            shadow="hover"
            @click="$router.push(`/houses/${house.id}`)"
          >
            <div class="house-image">
              <img :src="house.cover_image || '/default-house.jpg'" :alt="house.title" />
              <el-tag class="status-tag" :type="getHouseStatusType(house.status)">
                {{ getHouseStatusText(house.status) }}
              </el-tag>
            </div>
            <div class="house-info">
              <h3 class="house-title">{{ house.title }}</h3>
              <p class="house-address">
                <el-icon><Location /></el-icon>
                {{ house.address }}
              </p>
              <div class="house-details">
                <span>{{ house.house_type }}</span>
                <span>{{ house.area }}㎡</span>
                <span v-if="house.floor">{{ house.floor }}</span>
              </div>
              <div class="house-price">
                <span class="price">{{ formatPrice(house.price) }}</span>
                <span class="unit">万元</span>
                <span class="unit-price">{{ formatPrice(house.unit_price) }}元/㎡</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && hotHouses.length === 0" description="暂无房源" />
    </div>

    <!-- 数据统计 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="在售房源" :value="stats.total_houses">
              <template #prefix>
                <el-icon><House /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="平均价格" :value="stats.avg_price" suffix="万元">
              <template #prefix>
                <el-icon><Money /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="成交记录" :value="stats.total_transactions">
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="注册用户" :value="stats.total_users">
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHotHouses, getDistrictList } from '@/api/house'
import { formatPrice, getHouseStatusText, getHouseStatusType } from '@/utils'

const router = useRouter()
const loading = ref(false)
const hotHouses = ref([])
const districts = ref([])

const searchForm = reactive({
  search: '',
  district: '',
  house_type: ''
})

const banners = [
  {
    id: 1,
    title: '找到理想的家',
    description: '海量优质房源，专业服务团队',
    image: 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1200'
  },
  {
    id: 2,
    title: '数据驱动决策',
    description: '全面的市场分析，精准的价格预测',
    image: 'https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=1200'
  },
  {
    id: 3,
    title: '安全可靠',
    description: '实名认证，交易保障',
    image: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200'
  }
]

const stats = reactive({
  total_houses: 0,
  avg_price: 0,
  total_transactions: 0,
  total_users: 0
})

async function fetchHotHouses() {
  loading.value = true
  try {
    const res = await getHotHouses({ limit: 8 })
    console.log('热门房源API响应:', res)
    if (res.code === 200) {
      hotHouses.value = res.data.results || res.data
      console.log('热门房源数据:', hotHouses.value)
      if (hotHouses.value.length > 0) {
        console.log('第一个房源的封面图:', hotHouses.value[0].cover_image)
      }
    }
  } catch (error) {
    console.error('获取热门房源失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchDistricts() {
  try {
    const res = await getDistrictList()
    console.log('区域列表API响应:', res)
    if (res.code === 200) {
      // 处理多种可能的响应格式
      if (Array.isArray(res.data)) {
        districts.value = res.data
      } else if (res.data.results) {
        districts.value = res.data.results
      } else {
        districts.value = []
      }
      console.log('区域数据:', districts.value)
    }
  } catch (error) {
    console.error('获取区域列表失败:', error)
  }
}

function handleSearch() {
  router.push({
    path: '/houses',
    query: searchForm
  })
}

onMounted(() => {
  fetchHotHouses()
  fetchDistricts()
  
  // 模拟统计数据
  stats.total_houses = 1234
  stats.avg_price = 328.5
  stats.total_transactions = 567
  stats.total_users = 8901
})
</script>

<style lang="scss" scoped>
.home-page {
  .banner {
    margin-bottom: 30px;
    border-radius: 8px;
    overflow: hidden;

    .banner-item {
      width: 100%;
      height: 100%;
      background-size: cover;
      background-position: center;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.3);
      }

      .banner-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        color: #fff;
        z-index: 1;

        h1 {
          font-size: 48px;
          margin-bottom: 20px;
          font-weight: bold;
        }

        p {
          font-size: 20px;
        }
      }
    }
  }

  .search-section {
    margin-bottom: 40px;

    :deep(.el-card__body) {
      padding: 20px;
    }
  }

  .hot-houses-section {
    margin-bottom: 40px;

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      h2 {
        font-size: 24px;
        color: #303133;
      }
    }

    .house-card {
      margin-bottom: 20px;
      cursor: pointer;
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-5px);
      }

      .house-image {
        position: relative;
        height: 200px;
        overflow: hidden;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .status-tag {
          position: absolute;
          top: 10px;
          right: 10px;
        }
      }

      .house-info {
        padding: 15px;

        .house-title {
          font-size: 16px;
          color: #303133;
          margin-bottom: 8px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .house-address {
          font-size: 14px;
          color: #909399;
          margin-bottom: 10px;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .house-details {
          display: flex;
          gap: 10px;
          margin-bottom: 10px;
          font-size: 14px;
          color: #606266;

          span {
            padding: 2px 8px;
            background: #f5f7fa;
            border-radius: 4px;
          }
        }

        .house-price {
          display: flex;
          align-items: baseline;
          gap: 5px;

          .price {
            font-size: 24px;
            color: #f56c6c;
            font-weight: bold;
          }

          .unit {
            font-size: 14px;
            color: #f56c6c;
          }

          .unit-price {
            font-size: 12px;
            color: #909399;
            margin-left: auto;
          }
        }
      }
    }
  }

  .stats-section {
    .stat-card {
      text-align: center;

      :deep(.el-statistic__head) {
        font-size: 14px;
        color: #909399;
      }

      :deep(.el-statistic__content) {
        font-size: 28px;
        color: #409eff;
      }
    }
  }
}
</style>

