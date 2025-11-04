<template>
  <div class="location-picker">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>选择房源位置</span>
          <el-button 
            v-if="selectedLocation" 
            type="primary" 
            size="small"
            @click="confirmLocation"
          >
            确认位置
          </el-button>
        </div>
      </template>

      <!-- 地址搜索 -->
      <div class="search-box">
        <el-input
          v-model="searchAddress"
          placeholder="输入地址搜索（例如：上海市浦东新区张江高科技园区）"
          clearable
          @keyup.enter="searchLocation"
        >
          <template #append>
            <el-button @click="searchLocation" :loading="searching">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </template>
        </el-input>
        <div class="search-tip">
          点击地图任意位置选择房源位置，或使用搜索功能定位地址
        </div>
      </div>

      <!-- 当前选择的坐标信息 -->
      <div v-if="selectedLocation" class="location-info">
        <el-tag type="success" size="large">
          <el-icon><LocationFilled /></el-icon>
          经度: {{ selectedLocation.lng.toFixed(6) }}, 
          纬度: {{ selectedLocation.lat.toFixed(6) }}
        </el-tag>
        <el-tag v-if="selectedAddress" type="info" size="large" style="margin-left: 10px">
          {{ selectedAddress }}
        </el-tag>
      </div>

      <!-- 地图容器 -->
      <div ref="mapContainer" class="map-container"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  // 初始经纬度
  longitude: {
    type: Number,
    default: null
  },
  latitude: {
    type: Number,
    default: null
  },
  // 初始地址
  address: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:longitude', 'update:latitude', 'confirm'])

const mapContainer = ref(null)
let map = null
let marker = null

const searchAddress = ref(props.address || '')
const searching = ref(false)
const selectedLocation = ref(null)
const selectedAddress = ref('')

// 初始化选中的位置
if (props.longitude && props.latitude) {
  selectedLocation.value = {
    lng: props.longitude,
    lat: props.latitude
  }
}

// 修复 Leaflet 默认图标问题
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png'
})

// 初始化地图
function initMap() {
  if (!mapContainer.value) return

  // 默认中心点（上海）
  let center = [31.2304, 121.4737]
  let zoom = 12

  // 如果有初始坐标，使用初始坐标作为中心
  if (props.latitude && props.longitude) {
    center = [props.latitude, props.longitude]
    zoom = 15
  }

  // 创建地图
  map = L.map(mapContainer.value, {
    center: center,
    zoom: zoom,
    zoomControl: true
  })

  // 添加瓦片层（使用OpenStreetMap）
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map)

  // 如果有初始坐标，添加标记
  if (props.latitude && props.longitude) {
    addMarker([props.latitude, props.longitude])
  }

  // 监听地图点击事件
  map.on('click', handleMapClick)
}

// 处理地图点击
function handleMapClick(e) {
  const { lat, lng } = e.latlng
  
  selectedLocation.value = { lat, lng }
  
  // 更新标记
  addMarker([lat, lng])
  
  // 发送更新事件
  emit('update:longitude', lng)
  emit('update:latitude', lat)
  
  // 尝试反向地理编码获取地址（可选）
  reverseGeocode(lat, lng)
  
  ElMessage.success('已选择位置')
}

// 添加或更新标记
function addMarker(latlng) {
  if (marker) {
    marker.setLatLng(latlng)
  } else {
    marker = L.marker(latlng, {
      draggable: true
    }).addTo(map)
    
    // 监听标记拖拽
    marker.on('dragend', function(e) {
      const position = marker.getLatLng()
      selectedLocation.value = {
        lat: position.lat,
        lng: position.lng
      }
      emit('update:longitude', position.lng)
      emit('update:latitude', position.lat)
      reverseGeocode(position.lat, position.lng)
    })
  }
  
  // 地图居中到标记位置
  map.setView(latlng, 15)
}

// 搜索位置
async function searchLocation() {
  if (!searchAddress.value.trim()) {
    ElMessage.warning('请输入搜索地址')
    return
  }

  searching.value = true
  
  try {
    // 使用 Nominatim API 进行地理编码
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchAddress.value)}&limit=1`
    )
    
    const data = await response.json()
    
    if (data && data.length > 0) {
      const result = data[0]
      const lat = parseFloat(result.lat)
      const lng = parseFloat(result.lon)
      
      selectedLocation.value = { lat, lng }
      selectedAddress.value = result.display_name
      
      addMarker([lat, lng])
      
      emit('update:longitude', lng)
      emit('update:latitude', lat)
      
      ElMessage.success('搜索成功')
    } else {
      ElMessage.warning('未找到该地址，请尝试更详细的地址或直接在地图上点击')
    }
  } catch (error) {
    console.error('地址搜索失败:', error)
    ElMessage.error('搜索失败，请直接在地图上点击选择位置')
  } finally {
    searching.value = false
  }
}

// 反向地理编码（将坐标转换为地址）
async function reverseGeocode(lat, lng) {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
    )
    
    const data = await response.json()
    
    if (data && data.display_name) {
      selectedAddress.value = data.display_name
    }
  } catch (error) {
    console.error('反向地理编码失败:', error)
  }
}

// 确认位置
function confirmLocation() {
  if (selectedLocation.value) {
    emit('confirm', {
      longitude: selectedLocation.value.lng,
      latitude: selectedLocation.value.lat,
      address: selectedAddress.value
    })
    ElMessage.success('位置已确认')
  }
}

// 监听外部坐标变化
watch(() => [props.longitude, props.latitude], ([lng, lat]) => {
  if (lng && lat && map) {
    selectedLocation.value = { lng, lat }
    addMarker([lat, lng])
  }
})

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style lang="scss" scoped>
.location-picker {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    span {
      font-weight: bold;
      font-size: 16px;
    }
  }

  .search-box {
    margin-bottom: 15px;
    
    .search-tip {
      margin-top: 8px;
      font-size: 12px;
      color: #909399;
    }
  }

  .location-info {
    margin-bottom: 15px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
  }

  .map-container {
    width: 100%;
    height: 500px;
    border-radius: 4px;
    overflow: hidden;
  }
}
</style>

