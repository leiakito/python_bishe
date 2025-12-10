<template>
  <div class="house-detail-page" v-loading="loading">
    <el-card v-if="house">
      <!-- 房源图片 -->
      <div class="house-gallery">
        <el-carousel height="500px" indicator-position="outside">
          <el-carousel-item v-for="(image, index) in houseImages" :key="index">
            <img :src="image" :alt="`房源图片${index + 1}`" />
          </el-carousel-item>
        </el-carousel>
      </div>

      <!-- 房源基本信息 -->
      <div class="house-header">
        <div class="house-title-section">
          <h1>{{ house.title }}</h1>
          <el-tag :type="getHouseStatusType(house.status)">
            {{ getHouseStatusText(house.status) }}
          </el-tag>
        </div>
        
        <div class="house-price-section">
          <div class="total-price">
            <span class="price">{{ formatPrice(house.price) }}</span>
            <span class="unit">万元</span>
          </div>
          <div class="unit-price">
            单价: {{ formatPrice(house.unit_price) }} 元/㎡
          </div>
        </div>

        <div class="house-actions">
          <el-button
            :type="isPurchased ? 'success' : 'danger'"
            :icon="isPurchased ? 'CircleCheck' : 'ShoppingCart'"
            size="large"
            @click="handlePurchase"
            :disabled="house.status !== 'available' || isPurchased"
          >
            {{ isPurchased ? '已购买' : '立即购买' }}
          </el-button>
          <el-button
            :type="isFavorited ? 'warning' : 'default'"
            :icon="isFavorited ? 'StarFilled' : 'Star'"
            @click="handleFavorite"
          >
            {{ isFavorited ? '已收藏' : '收藏' }}
          </el-button>
          <el-button type="primary" icon="Bell" @click="showAlertDialog = true">
            价格提醒
          </el-button>
          <el-button icon="Share" @click="handleShare">分享</el-button>
        </div>
      </div>

      <!-- 房源详细信息 -->
      <el-row :gutter="20" class="house-info-section">
        <el-col :span="16">
          <el-card header="房源信息">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="户型">
                {{ house.house_type }}
              </el-descriptions-item>
              <el-descriptions-item label="面积">
                {{ house.area }} ㎡
              </el-descriptions-item>
              <el-descriptions-item label="楼层">
                {{ house.floor }} / {{ house.total_floors }} 层
              </el-descriptions-item>
              <el-descriptions-item label="朝向">
                {{ house.orientation }}
              </el-descriptions-item>
              <el-descriptions-item label="区域">
                {{ house.district_name }}
              </el-descriptions-item>
              <el-descriptions-item label="地址">
                {{ house.address }}
              </el-descriptions-item>
              <el-descriptions-item label="发布时间">
                {{ formatDate(house.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="浏览量">
                {{ house.views }} 次
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card header="房源描述" style="margin-top: 20px">
            <p class="house-description">{{ house.description || '暂无描述' }}</p>
          </el-card>

          <!-- 地图位置 -->
          <el-card header="位置信息" style="margin-top: 20px">
            <div id="map" style="height: 400px"></div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 经纪人信息 -->
          <el-card header="经纪人信息" v-if="house.agent">
            <div class="agent-info">
              <el-avatar :size="60">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="agent-details">
                <h3>{{ house.agent.real_name || house.agent.username }}</h3>
                <p v-if="house.agent.company">{{ house.agent.company }}</p>
                <p>{{ house.agent.phone }}</p>
              </div>
              <el-button type="primary" style="width: 100%; margin-top: 15px">
                <el-icon><Phone /></el-icon>
                联系经纪人
              </el-button>
            </div>
          </el-card>

          <!-- 推荐房源 -->
          <el-card header="推荐房源" style="margin-top: 20px">
            <div class="recommend-house" v-for="item in recommendHouses" :key="item.id">
              <img :src="item.cover_image || '/default-house.jpg'" :alt="item.title" />
              <div class="recommend-info">
                <h4>{{ item.title }}</h4>
                <p class="price">{{ formatPrice(item.price) }}万</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 价格提醒对话框 -->
    <el-dialog
      v-model="showAlertDialog"
      title="设置价格提醒"
      width="400px"
    >
      <el-form :model="alertForm" label-width="100px">
        <el-form-item label="当前价格">
          <el-input :value="house?.price + ' 万元'" disabled />
        </el-form-item>
        <el-form-item label="目标价格">
          <el-input-number
            v-model="alertForm.target_price"
            :min="0"
            :step="10"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item>
          <el-alert
            title="当房源价格低于或等于目标价格时，系统将通知您"
            type="info"
            :closable="false"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAlertDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateAlert">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分享对话框 -->
    <el-dialog
      v-model="showShareDialog"
      title="分享房源"
      width="450px"
      @open="handleDialogOpen"
    >
      <div class="share-container">
        <!-- 分享链接 -->
        <div class="share-link-section">
          <el-alert
            title="复制链接分享给好友"
            type="info"
            :closable="false"
            style="margin-bottom: 20px"
          />
          <el-input
            v-model="shareUrl"
            readonly
            ref="shareUrlInput"
          >
            <template #append>
              <el-button @click="copyShareUrl">
                <el-icon><DocumentCopy /></el-icon>
                复制
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- 二维码显示 -->
        <div class="qrcode-section">
          <el-divider>扫描二维码</el-divider>
          <div class="qrcode-container">
            <div ref="qrcodeElement" class="qrcode"></div>
            <p class="qrcode-tip">扫描二维码查看房源详情</p>
          </div>
        </div>

        <!-- 分享信息预览 -->
        <div class="share-preview">
          <el-divider>房源信息</el-divider>
          <div class="preview-card">
            <img 
              :src="house?.cover_image || 'https://via.placeholder.com/120x90?text=No+Image'" 
              alt="房源图片"
              @error="handleImageError"
            />
            <div class="preview-info">
              <h4>{{ house?.title }}</h4>
              <p class="preview-price">{{ formatPrice(house?.price) }} 万元</p>
              <p class="preview-desc">{{ house?.address }}</p>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getHouseDetail, getHouseList } from '@/api/house'
import { toggleFavorite, checkFavorite, createPriceAlert, checkHouseAlert } from '@/api/favorite'
import { useUserStore } from '@/stores/user'
import { formatPrice, formatDate, getHouseStatusText, getHouseStatusType } from '@/utils'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const house = ref(null)
const isFavorited = ref(false)
const isPurchased = ref(false)
const recommendHouses = ref([])
const showAlertDialog = ref(false)
const showShareDialog = ref(false)
const shareUrl = ref('')
const shareUrlInput = ref(null)
const qrcodeElement = ref(null)

let map = null

const alertForm = reactive({
  target_price: 0
})

const houseImages = computed(() => {
  if (!house.value) return []
  const images = [house.value.cover_image]
  if (house.value.images && house.value.images.length > 0) {
    images.push(...house.value.images.map(img => img.image))
  }
  return images.filter(Boolean)
})

async function fetchHouseDetail() {
  loading.value = true
  try {
    const res = await getHouseDetail(route.params.id)
    if (res.code === 200) {
      house.value = res.data
      alertForm.target_price = res.data.price
      
      // 检查购买状态
      checkPurchaseStatus()
      
      // 检查收藏状态和价格提醒
      if (userStore.isLoggedIn) {
        checkFavoriteStatus()
        checkPriceAlert()
      }
      
      // 获取推荐房源
      fetchRecommendHouses()
      
      // 初始化地图
      setTimeout(() => {
        initMap()
      }, 100)
    }
  } catch (error) {
    console.error('获取房源详情失败:', error)
    ElMessage.error('房源不存在')
    router.push('/houses')
  } finally {
    loading.value = false
  }
}

// 检查购买状态
function checkPurchaseStatus() {
  const purchasedHouses = JSON.parse(localStorage.getItem('purchasedHouses') || '[]')
  isPurchased.value = purchasedHouses.includes(route.params.id)
}

// 处理购买
async function handlePurchase() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再购买')
    router.push('/login')
    return
  }

  if (house.value.status !== 'available') {
    ElMessage.warning('该房源当前不可购买')
    return
  }

  // 显示确认对话框
  try {
    await ElMessageBox.confirm(
      `确认购买此房源？\n\n房源：${house.value.title}\n价格：${formatPrice(house.value.price)} 万元\n地址：${house.value.address}`,
      '确认购买',
      {
        confirmButtonText: '确认购买',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )

    // 模拟购买处理
    const purchasedHouses = JSON.parse(localStorage.getItem('purchasedHouses') || '[]')
    
    if (!purchasedHouses.includes(route.params.id)) {
      purchasedHouses.push(route.params.id)
      localStorage.setItem('purchasedHouses', JSON.stringify(purchasedHouses))
      
      // 保存购买详情
      const purchaseDetails = JSON.parse(localStorage.getItem('purchaseDetails') || '{}')
      purchaseDetails[route.params.id] = {
        houseId: house.value.id,
        title: house.value.title,
        price: house.value.price,
        address: house.value.address,
        purchaseDate: new Date().toISOString(),
        userId: userStore.userInfo?.id
      }
      localStorage.setItem('purchaseDetails', JSON.stringify(purchaseDetails))
    }

    isPurchased.value = true

    // 显示成功消息
    ElNotification({
      title: '🎉 购买成功',
      message: `恭喜您成功购买房源！\n房源：${house.value.title}\n价格：${formatPrice(house.value.price)} 万元\n\n我们的工作人员将尽快与您联系。`,
      type: 'success',
      duration: 6000,
      position: 'top-right'
    })

  } catch (error) {
    if (error !== 'cancel') {
      console.error('购买失败:', error)
    }
  }
}

async function checkFavoriteStatus() {
  try {
    const res = await checkFavorite({ house: route.params.id })
    if (res.code === 200) {
      isFavorited.value = res.data.is_favorited
    }
  } catch (error) {
    console.error('检查收藏状态失败:', error)
  }
}

// 检查价格提醒
async function checkPriceAlert() {
  try {
    const res = await checkHouseAlert({ house_id: route.params.id })
    if (res.code === 200 && res.data.has_alert) {
      const alertData = res.data
      
      // 如果价格提醒已触发，显示通知
      if (alertData.triggered) {
        ElNotification({
          title: '🎉 价格提醒',
          message: `好消息！您关注的房源价格已降至 ${alertData.current_price} 万元，达到您的目标价格 ${alertData.target_price} 万元！`,
          type: 'success',
          duration: 8000,
          position: 'top-right'
        })
      } else if (alertData.status === 'active') {
        // 显示当前价格与目标价格的差距
        const priceDiff = (alertData.current_price - alertData.target_price).toFixed(2)
        if (priceDiff > 0) {
          ElNotification({
            title: '💡 价格提醒',
            message: `您设置的目标价格为 ${alertData.target_price} 万元，当前价格 ${alertData.current_price} 万元，还需降价 ${priceDiff} 万元`,
            type: 'info',
            duration: 5000,
            position: 'top-right'
          })
        }
      }
    }
  } catch (error) {
    console.error('检查价格提醒失败:', error)
  }
}

async function fetchRecommendHouses() {
  try {
    const res = await getHouseList({
      district: house.value.district,
      limit: 5
    })
    if (res.code === 200) {
      recommendHouses.value = (res.data.results || res.data)
        .filter(item => item.id !== house.value.id)
        .slice(0, 4)
    }
  } catch (error) {
    console.error('获取推荐房源失败:', error)
  }
}

async function handleFavorite() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const res = await toggleFavorite({ house: house.value.id })
    if (res.code === 200) {
      isFavorited.value = !isFavorited.value
      ElMessage.success(isFavorited.value ? '收藏成功' : '取消收藏')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleCreateAlert() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  if (alertForm.target_price <= 0) {
    ElMessage.warning('请输入有效的目标价格')
    return
  }

  try {
    const res = await createPriceAlert({
      house_id: house.value.id,
      target_price: alertForm.target_price
    })
    if (res.code === 201 || res.code === 200) {
      ElMessage.success('价格提醒设置成功')
      showAlertDialog.value = false
      alertForm.target_price = house.value.price
    } else {
      ElMessage.error(res.msg || '设置失败')
    }
  } catch (error) {
    console.error('价格提醒创建失败:', error)
    let errorMsg = '设置失败'
    if (error.response && error.response.data) {
      const data = error.response.data
      if (typeof data === 'object') {
        const firstError = Object.values(data)[0]
        if (Array.isArray(firstError)) {
          errorMsg = firstError[0]
        } else if (typeof firstError === 'string') {
          errorMsg = firstError
        } else {
          errorMsg = data.msg || data.detail || errorMsg
        }
      }
    }
    ElMessage.error(errorMsg)
  }
}

// 分享功能
function handleShare() {
  showShareDialog.value = true
}

async function handleDialogOpen() {
  // 生成分享链接
  const baseUrl = window.location.origin
  shareUrl.value = `${baseUrl}/houses/${route.params.id}`
  
  // 生成二维码
  await generateQRCode()
}

async function copyShareUrl() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    // 降级方案：使用传统方法复制
    const input = shareUrlInput.value?.$el?.querySelector('input')
    if (input) {
      input.select()
      document.execCommand('copy')
      ElMessage.success('链接已复制到剪贴板')
    } else {
      ElMessage.error('复制失败，请手动复制')
    }
  }
}

async function generateQRCode() {
  // 等待DOM更新
  await new Promise(resolve => setTimeout(resolve, 100))
  
  if (!qrcodeElement.value) return
  
  // 清除旧的二维码
  qrcodeElement.value.innerHTML = ''
  
  try {
    // 动态导入qrcode库
    const QRCode = (await import('qrcode')).default
    
    // 创建canvas元素
    const canvas = document.createElement('canvas')
    
    // 生成二维码到canvas
    await QRCode.toCanvas(canvas, shareUrl.value, {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    })
    
    // 将canvas添加到容器中
    qrcodeElement.value.appendChild(canvas)
  } catch (error) {
    console.error('生成二维码失败:', error)
    ElMessage.error('生成二维码失败')
  }
}

function initMap() {
  // 如果地图已存在，先销毁
  if (map) {
    map.remove()
    map = null
  }

  // 检查房源是否有坐标
  if (!house.value || !house.value.latitude || !house.value.longitude) {
    console.warn('房源缺少坐标信息')
    return
  }

  const lat = parseFloat(house.value.latitude)
  const lng = parseFloat(house.value.longitude)

  // 验证坐标是否有效
  if (isNaN(lat) || isNaN(lng)) {
    console.warn('房源坐标无效:', house.value.latitude, house.value.longitude)
    return
  }

  // 初始化地图
  map = L.map('map').setView([lat, lng], 15)

  // 添加地图图层
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(map)

  // 配置标记图标
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png'
  })

  // 添加标记
  const marker = L.marker([lat, lng]).addTo(map)
  marker.bindPopup(`
    <div style="min-width: 200px">
      <h4 style="margin: 0 0 10px 0">${house.value.title}</h4>
      <p style="margin: 5px 0; color: #666">${house.value.address}</p>
      <p style="margin: 5px 0">
        <strong style="color: #f56c6c; font-size: 18px">${formatPrice(house.value.price)}万</strong>
      </p>
    </div>
  `).openPopup()
}

function handleImageError(e) {
  e.target.src = 'https://via.placeholder.com/120x90?text=No+Image'
}

onMounted(() => {
  fetchHouseDetail()
})

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})
</script>

<style lang="scss" scoped>
.house-detail-page {
  .house-gallery {
    margin-bottom: 20px;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .house-header {
    padding: 20px 0;
    border-bottom: 1px solid #e4e7ed;

    .house-title-section {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 15px;

      h1 {
        font-size: 28px;
        color: #303133;
        margin: 0;
      }
    }

    .house-price-section {
      margin-bottom: 15px;

      .total-price {
        .price {
          font-size: 36px;
          color: #f56c6c;
          font-weight: bold;
        }

        .unit {
          font-size: 18px;
          color: #f56c6c;
          margin-left: 5px;
        }
      }

      .unit-price {
        font-size: 14px;
        color: #909399;
        margin-top: 5px;
      }
    }

    .house-actions {
      display: flex;
      gap: 10px;
      
      .el-button {
        &:first-child {
          // 购买按钮样式
          font-size: 16px;
          font-weight: 600;
          padding: 15px 30px;
          
          &.el-button--danger {
            background: linear-gradient(135deg, #f56c6c 0%, #e04949 100%);
            border: none;
            box-shadow: 0 4px 12px rgba(245, 108, 108, 0.4);
            
            &:hover {
              box-shadow: 0 6px 16px rgba(245, 108, 108, 0.5);
              transform: translateY(-2px);
              transition: all 0.3s;
            }
          }
          
          &.el-button--success {
            background: linear-gradient(135deg, #67c23a 0%, #5daf34 100%);
            border: none;
            cursor: not-allowed;
          }
          
          &:disabled {
            opacity: 0.7;
          }
        }
      }
    }
  }

  .house-info-section {
    margin-top: 20px;

    .house-description {
      line-height: 1.8;
      color: #606266;
      white-space: pre-wrap;
    }

    .agent-info {
      text-align: center;

      .agent-details {
        margin-top: 15px;

        h3 {
          font-size: 18px;
          color: #303133;
          margin-bottom: 5px;
        }

        p {
          font-size: 14px;
          color: #909399;
          margin: 5px 0;
        }
      }
    }

    .recommend-house {
      display: flex;
      gap: 10px;
      margin-bottom: 15px;
      cursor: pointer;

      &:hover {
        opacity: 0.8;
      }

      img {
        width: 80px;
        height: 60px;
        object-fit: cover;
        border-radius: 4px;
      }

      .recommend-info {
        flex: 1;

        h4 {
          font-size: 14px;
          color: #303133;
          margin-bottom: 5px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .price {
          font-size: 16px;
          color: #f56c6c;
          font-weight: bold;
        }
      }
    }
  }
}

// 分享对话框样式
.share-container {
  .share-link-section {
    margin-bottom: 30px;
  }

  .qrcode-section {
    margin-bottom: 20px;
    
    .qrcode-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 0;

      .qrcode {
        canvas {
          border: 1px solid #e4e7ed;
          border-radius: 8px;
          padding: 10px;
          background: white;
        }
      }

      .qrcode-tip {
        margin-top: 15px;
        font-size: 14px;
        color: #909399;
      }
    }
  }

  .share-preview {
    .preview-card {
      display: flex;
      gap: 15px;
      padding: 15px;
      background: #f5f7fa;
      border-radius: 8px;
      transition: all 0.3s;

      &:hover {
        background: #ecf5ff;
      }

      img {
        width: 120px;
        height: 90px;
        object-fit: cover;
        border-radius: 4px;
      }

      .preview-info {
        flex: 1;

        h4 {
          font-size: 16px;
          color: #303133;
          margin-bottom: 8px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .preview-price {
          font-size: 20px;
          color: #f56c6c;
          font-weight: bold;
          margin-bottom: 5px;
        }

        .preview-desc {
          font-size: 13px;
          color: #909399;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }
  }
}
</style>

