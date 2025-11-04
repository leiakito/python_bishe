<template>
  <div class="map-page">
    <div class="page-title">地图找房</div>

    <el-card>
      <!-- 筛选条件 -->
      <div class="map-filter">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="区域">
            <el-select
              v-model="filterForm.district"
              placeholder="选择区域"
              clearable
              style="width: 150px"
              @change="fetchMapData"
            >
              <el-option
                v-for="district in districts"
                :key="district.id"
                :label="district.name"
                :value="district.id"
              />
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

          <el-form-item>
            <el-button type="primary" @click="fetchMapData">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 地图容器 -->
      <div class="map-container" v-loading="loading">
        <div id="map" ref="mapRef"></div>
        
        <!-- 房源列表侧边栏 -->
        <div class="house-sidebar" v-if="selectedHouse">
          <el-card :body-style="{ padding: '0' }">
            <div class="house-image">
              <img
                :src="selectedHouse.cover_image || '/default-house.jpg'"
                :alt="selectedHouse.title"
              />
            </div>
            <div class="house-info">
              <h3>{{ selectedHouse.title }}</h3>
              <p class="address">
                <el-icon><Location /></el-icon>
                {{ selectedHouse.address }}
              </p>
              <div class="details">
                <span>{{ selectedHouse.house_type }}</span>
                <span>{{ selectedHouse.area }}㎡</span>
              </div>
              <div class="price">
                <span class="total">{{ formatPrice(selectedHouse.price) }}万</span>
                <span class="unit">{{ formatPrice(selectedHouse.unit_price) }}元/㎡</span>
              </div>
              <el-button
                type="primary"
                style="width: 100%; margin-top: 10px"
                @click="goToDetail(selectedHouse.id)"
              >
                查看详情
              </el-button>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="map-stats">
        <el-statistic title="地图房源数" :value="houseCount">
          <template #prefix>
            <el-icon><House /></el-icon>
          </template>
        </el-statistic>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMapData, getDistrictList } from '@/api/house'
import { formatPrice } from '@/utils'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()
const loading = ref(false)
const mapRef = ref(null)
const districts = ref([])
const selectedHouse = ref(null)
const houseCount = ref(0)

let map = null
let markers = []

const filterForm = reactive({
  district: '',
  min_price: null,
  max_price: null
})

async function fetchDistricts() {
  try {
    const res = await getDistrictList()
    if (res.code === 200) {
      // 处理多种可能的响应格式
      if (Array.isArray(res.data)) {
        districts.value = res.data
      } else if (res.data.results) {
        districts.value = res.data.results
      } else {
        districts.value = []
      }
    }
  } catch (error) {
    console.error('获取区域列表失败:', error)
  }
}

async function fetchMapData() {
  loading.value = true
  try {
    const params = {}
    if (filterForm.district) params.district = filterForm.district
    if (filterForm.min_price) params.min_price = filterForm.min_price
    if (filterForm.max_price) params.max_price = filterForm.max_price

    const res = await getMapData(params)
    console.log('地图API响应:', res)
    if (res.code === 200) {
      const data = res.data
      houseCount.value = data.features?.length || 0
      console.log('地图房源数量:', houseCount.value)
      if (data.features && data.features.length > 0) {
        console.log('第一个房源数据:', data.features[0].properties)
      }
      renderMarkers(data)
    }
  } catch (error) {
    console.error('获取地图数据失败:', error)
  } finally {
    loading.value = false
  }
}

function initMap() {
  // 初始化地图 (以北京为中心)
  map = L.map('map').setView([39.9042, 116.4074], 11)

  // 添加地图图层
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(map)

  // 自定义标记图标
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png'
  })
}

function renderMarkers(geojson) {
  // 清除旧标记
  markers.forEach(marker => map.removeLayer(marker))
  markers = []

  if (!geojson.features || geojson.features.length === 0) {
    return
  }

  // 添加新标记
  geojson.features.forEach(feature => {
    const { coordinates } = feature.geometry
    const { properties } = feature

    const marker = L.marker([coordinates[1], coordinates[0]])
      .addTo(map)
      .bindPopup(`
        <div style="min-width: 200px">
          <h4 style="margin: 0 0 10px 0">${properties.title}</h4>
          <p style="margin: 5px 0; color: #666">${properties.address}</p>
          <p style="margin: 5px 0">
            <strong style="color: #f56c6c; font-size: 18px">${formatPrice(properties.price)}万</strong>
          </p>
          <p style="margin: 5px 0; font-size: 12px; color: #999">
            ${properties.house_type} | ${properties.area}㎡
          </p>
        </div>
      `)

    marker.on('click', () => {
      selectedHouse.value = properties
    })

    markers.push(marker)
  })

  // 调整地图视图以显示所有标记
  if (markers.length > 0) {
    const group = L.featureGroup(markers)
    map.fitBounds(group.getBounds().pad(0.1))
  }
}

function goToDetail(id) {
  router.push(`/houses/${id}`)
}

onMounted(() => {
  fetchDistricts()
  initMap()
  fetchMapData()
})

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})
</script>

<style lang="scss" scoped>
.map-page {
  .map-filter {
    margin-bottom: 20px;
  }

  .map-container {
    position: relative;
    height: 600px;

    #map {
      width: 100%;
      height: 100%;
      border-radius: 4px;
    }

    .house-sidebar {
      position: absolute;
      top: 20px;
      right: 20px;
      width: 300px;
      z-index: 1000;

      .house-image {
        height: 200px;
        overflow: hidden;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }

      .house-info {
        padding: 15px;

        h3 {
          font-size: 16px;
          color: #303133;
          margin-bottom: 10px;
        }

        .address {
          font-size: 14px;
          color: #909399;
          margin-bottom: 10px;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .details {
          display: flex;
          gap: 10px;
          margin-bottom: 10px;

          span {
            padding: 2px 8px;
            background: #f5f7fa;
            border-radius: 4px;
            font-size: 12px;
          }
        }

        .price {
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          margin-bottom: 10px;

          .total {
            font-size: 24px;
            color: #f56c6c;
            font-weight: bold;
          }

          .unit {
            font-size: 12px;
            color: #909399;
          }
        }
      }
    }
  }

  .map-stats {
    margin-top: 20px;
    text-align: center;
  }
}
</style>

