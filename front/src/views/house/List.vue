<template>
  <div class="house-list-page">
    <div class="page-title">房源列表</div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.search"
            placeholder="搜索标题、地址"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="区域">
          <el-select
            v-model="filterForm.district"
            placeholder="选择区域"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="district in districts"
              :key="district.id"
              :label="district.name"
              :value="district.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="户型">
          <el-select
            v-model="filterForm.house_type"
            placeholder="选择户型"
            clearable
            style="width: 120px"
          >
            <el-option label="1室" value="1室" />
            <el-option label="2室" value="2室" />
            <el-option label="3室" value="3室" />
            <el-option label="4室" value="4室" />
            <el-option label="5室及以上" value="5室及以上" />
          </el-select>
        </el-form-item>

        <el-form-item label="价格范围">
          <el-input-number
            v-model="filterForm.min_price"
            :min="0"
            :controls="false"
            placeholder="最低价"
            style="width: 120px"
          />
          <span style="margin: 0 10px">-</span>
          <el-input-number
            v-model="filterForm.max_price"
            :min="0"
            :controls="false"
            placeholder="最高价"
            style="width: 120px"
          />
        </el-form-item>

        <el-form-item label="面积范围">
          <el-input-number
            v-model="filterForm.min_area"
            :min="0"
            :controls="false"
            placeholder="最小面积"
            style="width: 120px"
          />
          <span style="margin: 0 10px">-</span>
          <el-input-number
            v-model="filterForm.max_area"
            :min="0"
            :controls="false"
            placeholder="最大面积"
            style="width: 120px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <div class="filter-actions">
        <el-radio-group v-model="filterForm.ordering" @change="handleSearch">
          <el-radio-button label="-created_at">最新发布</el-radio-button>
          <el-radio-button label="price">价格升序</el-radio-button>
          <el-radio-button label="-price">价格降序</el-radio-button>
          <el-radio-button label="area">面积升序</el-radio-button>
          <el-radio-button label="-area">面积降序</el-radio-button>
          <el-radio-button label="-views">浏览量</el-radio-button>
        </el-radio-group>
      </div>
    </el-card>

    <!-- 房源列表 -->
    <div class="house-list" v-loading="loading">
      <el-row :gutter="20">
        <el-col
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          v-for="house in houseList"
          :key="house.id"
        >
          <el-card
            class="house-card"
            :body-style="{ padding: '0' }"
            shadow="hover"
          >
            <div class="house-image" @click="goToDetail(house.id)">
              <img :src="house.cover_image || '/default-house.jpg'" :alt="house.title" />
              <el-tag class="status-tag" :type="getHouseStatusType(house.status)">
                {{ getHouseStatusText(house.status) }}
              </el-tag>
            </div>
            <div class="house-info">
              <h3 class="house-title" @click="goToDetail(house.id)">
                {{ house.title }}
              </h3>
              <p class="house-address">
                <el-icon><Location /></el-icon>
                {{ house.address }}
              </p>
              <div class="house-details">
                <span>{{ house.house_type }}</span>
                <span>{{ house.area }}㎡</span>
                <span>{{ house.floor }}/{{ house.total_floors }}层</span>
              </div>
              <div class="house-footer">
                <div class="house-price">
                  <span class="price">{{ formatPrice(house.price) }}</span>
                  <span class="unit">万</span>
                </div>
                <el-button
                  :icon="house.is_favorited ? 'StarFilled' : 'Star'"
                  :type="house.is_favorited ? 'warning' : 'default'"
                  circle
                  size="small"
                  @click="handleFavorite(house)"
                />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && houseList.length === 0" description="暂无房源" />

      <!-- 分页 -->
      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 36, 48]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getHouseList, getDistrictList } from '@/api/house'
import { toggleFavorite } from '@/api/favorite'
import { useUserStore } from '@/stores/user'
import { formatPrice, getHouseStatusText, getHouseStatusType } from '@/utils'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const houseList = ref([])
const districts = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const filterForm = reactive({
  search: '',
  district: '',
  house_type: '',
  min_price: null,
  max_price: null,
  min_area: null,
  max_area: null,
  status: 'available',
  ordering: '-created_at'
})

async function fetchHouseList() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filterForm
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })

    const res = await getHouseList(params)
    if (res.code === 200) {
      houseList.value = res.data.results || []
      total.value = res.data.count || 0
    }
  } catch (error) {
    console.error('获取房源列表失败:', error)
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
  currentPage.value = 1
  fetchHouseList()
}

function handleReset() {
  Object.assign(filterForm, {
    search: '',
    district: '',
    house_type: '',
    min_price: null,
    max_price: null,
    min_area: null,
    max_area: null,
    status: 'available',
    ordering: '-created_at'
  })
  handleSearch()
}

function handleSizeChange(val) {
  pageSize.value = val
  fetchHouseList()
}

function handleCurrentChange(val) {
  currentPage.value = val
  fetchHouseList()
}

function goToDetail(id) {
  router.push(`/houses/${id}`)
}

async function handleFavorite(house) {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const res = await toggleFavorite({ house: house.id })
    if (res.code === 200) {
      house.is_favorited = !house.is_favorited
      ElMessage.success(house.is_favorited ? '收藏成功' : '取消收藏')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 监听路由查询参数
watch(
  () => route.query,
  (query) => {
    if (query.search) filterForm.search = query.search
    if (query.district) filterForm.district = query.district
    if (query.house_type) filterForm.house_type = query.house_type
  },
  { immediate: true }
)

onMounted(() => {
  fetchDistricts()
  fetchHouseList()
})
</script>

<style lang="scss" scoped>
.house-list-page {
  .filter-card {
    margin-bottom: 20px;

    .filter-actions {
      margin-top: 15px;
      padding-top: 15px;
      border-top: 1px solid #e4e7ed;
    }
  }

  .house-list {
    .house-card {
      margin-bottom: 20px;
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-5px);
      }

      .house-image {
        position: relative;
        height: 200px;
        overflow: hidden;
        cursor: pointer;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.3s;
        }

        &:hover img {
          transform: scale(1.1);
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
          cursor: pointer;

          &:hover {
            color: #409eff;
          }
        }

        .house-address {
          font-size: 14px;
          color: #909399;
          margin-bottom: 10px;
          display: flex;
          align-items: center;
          gap: 4px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
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
            font-size: 12px;
          }
        }

        .house-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .house-price {
            .price {
              font-size: 24px;
              color: #f56c6c;
              font-weight: bold;
            }

            .unit {
              font-size: 14px;
              color: #f56c6c;
              margin-left: 2px;
            }
          }
        }
      }
    }

    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 30px;
    }
  }
}
</style>

