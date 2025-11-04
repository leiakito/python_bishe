<template>
  <div class="my-houses-page">
    <div class="page-title">我的房源</div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>房源管理</span>
          <el-button type="primary" icon="Plus" @click="showCreateDialog = true">
            发布房源
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选区域 -->
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="关键词">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索标题、地址"
              clearable
              style="width: 200px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="状态">
            <el-select
              v-model="searchForm.status"
              placeholder="全部状态"
              clearable
              style="width: 120px"
              @change="handleSearch"
            >
              <el-option label="在售" value="available" />
              <el-option label="已售" value="sold" />
              <el-option label="预定" value="reserved" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="户型">
            <el-select
              v-model="searchForm.house_type"
              placeholder="全部户型"
              clearable
              style="width: 120px"
              @change="handleSearch"
            >
              <el-option label="1室" value="1室" />
              <el-option label="2室" value="2室" />
              <el-option label="3室" value="3室" />
              <el-option label="4室" value="4室" />
              <el-option label="5室及以上" value="5室及以上" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleSearch">
              搜索
            </el-button>
            <el-button icon="Refresh" @click="handleReset">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="houseList" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="address" label="地址" min-width="150" />
        <el-table-column label="价格" width="120">
          <template #default="{ row }">
            {{ formatPrice(row.price) }}万
          </template>
        </el-table-column>
        <el-table-column prop="area" label="面积" width="100">
          <template #default="{ row }">
            {{ row.area }}㎡
          </template>
        </el-table-column>
        <el-table-column prop="house_type" label="户型" width="100" />
        <el-table-column label="状态" width="140">
          <template #default="{ row }">
            <el-select
              v-model="row.status"
              size="small"
              @change="handleStatusChange(row)"
            >
              <el-option label="在售" value="available">
                <el-tag type="success" size="small">在售</el-tag>
              </el-option>
              <el-option label="已售" value="sold">
                <el-tag type="info" size="small">已售</el-tag>
              </el-option>
              <el-option label="预定" value="reserved">
                <el-tag type="warning" size="small">预定</el-tag>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="浏览量" width="100">
          <template #default="{ row }">
            {{ row.views }}
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="$router.push(`/houses/${row.id}`)"
            >
              查看
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="handleManageImages(row)"
            >
              图片
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <el-empty v-if="!loading && houseList.length === 0" description="暂无房源" />
    </el-card>

    <!-- 创建/编辑房源对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑房源' : '发布房源'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="houseForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="houseForm.title" placeholder="请输入房源标题" />
        </el-form-item>
        <el-form-item label="所属区域" prop="district">
          <el-select 
            v-model="houseForm.district" 
            placeholder="请选择区域" 
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="district in districtList"
              :key="district.id"
              :label="`${district.city} - ${district.name}`"
              :value="district.id"
            >
              <span>{{ district.city }} - {{ district.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ district.house_count }} 套房源
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="详细地址" prop="address">
          <el-input v-model="houseForm.address" placeholder="请输入详细地址" />
        </el-form-item>
        <el-form-item label="建筑面积(㎡)" prop="area">
          <el-input-number 
            v-model="houseForm.area" 
            :min="0" 
            :precision="2"
            :step="1"
            style="width: 100%"
            @change="calculatePrice"
            placeholder="请输入建筑面积"
          />
        </el-form-item>
        <el-form-item label="单价(元/㎡)" prop="unit_price">
          <el-input-number 
            v-model="houseForm.unit_price" 
            :min="0" 
            :precision="2"
            :step="100"
            style="width: 100%"
            @change="calculatePriceFromUnit"
            placeholder="输入单价自动计算总价"
          />
          <template #extra>
            <span class="form-tip" v-if="houseForm.area > 0 && houseForm.unit_price > 0">
              预计总价：{{ ((houseForm.unit_price * houseForm.area) / 10000).toFixed(2) }} 万元
            </span>
          </template>
        </el-form-item>
        <el-form-item label="总价(万)" prop="price">
          <el-input-number 
            v-model="houseForm.price" 
            :min="0" 
            :precision="2"
            :step="10"
            style="width: 100%"
            @change="calculateUnitPrice"
            placeholder="输入总价自动计算单价"
          />
          <template #extra>
            <span class="form-tip" v-if="houseForm.area > 0 && houseForm.price > 0">
              预计单价：{{ ((houseForm.price * 10000) / houseForm.area).toFixed(2) }} 元/㎡
            </span>
          </template>
        </el-form-item>
        <el-form-item label="户型" prop="house_type">
          <el-select v-model="houseForm.house_type" placeholder="请选择户型" style="width: 100%">
            <el-option label="1室" value="1室" />
            <el-option label="2室" value="2室" />
            <el-option label="3室" value="3室" />
            <el-option label="4室" value="4室" />
            <el-option label="5室及以上" value="5室及以上" />
          </el-select>
        </el-form-item>
        <el-form-item label="楼层" prop="floor">
          <el-input v-model="houseForm.floor" placeholder="例如：中楼层" />
        </el-form-item>
        <el-form-item label="总楼层" prop="total_floors">
          <el-input-number 
            v-model="houseForm.total_floors" 
            :min="1" 
            :max="100"
            style="width: 100%" 
          />
        </el-form-item>
        <el-form-item label="朝向" prop="orientation">
          <el-select v-model="houseForm.orientation" placeholder="请选择朝向" style="width: 100%">
            <el-option label="东" value="东" />
            <el-option label="南" value="南" />
            <el-option label="西" value="西" />
            <el-option label="北" value="北" />
            <el-option label="东南" value="东南" />
            <el-option label="东北" value="东北" />
            <el-option label="西南" value="西南" />
            <el-option label="西北" value="西北" />
            <el-option label="南北" value="南北" />
          </el-select>
        </el-form-item>
        <el-form-item label="装修情况" prop="decoration">
          <el-input v-model="houseForm.decoration" placeholder="例如：精装修" />
        </el-form-item>
        <el-form-item label="建造年份" prop="build_year">
          <el-input-number 
            v-model="houseForm.build_year" 
            :min="1950" 
            :max="new Date().getFullYear()"
            style="width: 100%" 
          />
        </el-form-item>
        <el-form-item label="房源位置">
          <el-button 
            type="primary" 
            @click="showLocationPicker = true"
            :icon="houseForm.longitude && houseForm.latitude ? 'LocationFilled' : 'Location'"
          >
            {{ houseForm.longitude && houseForm.latitude ? '重新选择位置' : '在地图上选择位置' }}
          </el-button>
          <div v-if="houseForm.longitude && houseForm.latitude" style="margin-top: 8px;">
            <el-tag type="success">
              经度: {{ houseForm.longitude.toFixed(6) }}, 
              纬度: {{ houseForm.latitude.toFixed(6) }}
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="房源描述" prop="description">
          <el-input
            v-model="houseForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入房源详细描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 地图选点对话框 -->
    <el-dialog
      v-model="showLocationPicker"
      title="选择房源位置"
      width="900px"
      :close-on-click-modal="false"
    >
      <LocationPicker
        v-model:longitude="houseForm.longitude"
        v-model:latitude="houseForm.latitude"
        :address="houseForm.address"
        @confirm="handleLocationConfirm"
      />
      <template #footer>
        <el-button @click="showLocationPicker = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleLocationConfirm"
          :disabled="!houseForm.longitude || !houseForm.latitude"
        >
          确认位置
        </el-button>
      </template>
    </el-dialog>

    <!-- 图片管理对话框 -->
    <el-dialog
      v-model="showImageDialog"
      title="管理房源图片"
      width="800px"
    >
      <div class="image-manager">
        <el-upload
          :action="`/api/house-images/`"
          :headers="uploadHeaders"
          :data="{ house: currentHouse?.id, order: imageList.length }"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          name="image"
          list-type="picture-card"
          accept="image/*"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>

        <div class="image-list" v-if="imageList.length > 0">
          <div class="image-item" v-for="image in imageList" :key="image.id">
            <el-image
              :src="image.image"
              fit="cover"
              style="width: 148px; height: 148px"
            />
            <div class="image-actions">
              <el-button
                type="danger"
                size="small"
                icon="Delete"
                @click="handleDeleteImage(image)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>

        <el-empty v-else description="暂无图片" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { getHouseList, createHouse, updateHouse, patchHouse, deleteHouse, getDistrictList } from '@/api/house'
import { formatPrice, formatDate, getHouseStatusText, getHouseStatusType } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import request from '@/utils/request'
import LocationPicker from '@/components/LocationPicker.vue'

const loading = ref(false)
const houseList = ref([])
const districtList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({
  keyword: '',
  status: '',
  house_type: ''
})
const showCreateDialog = ref(false)
const showImageDialog = ref(false)
const showLocationPicker = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentHouse = ref(null)
const imageList = ref([])

// 上传请求头
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('access_token')
  return {
    'Authorization': `Bearer ${token}`
  }
})

const houseForm = reactive({
  id: null,
  title: '',
  district: null,
  address: '',
  price: 0,
  unit_price: 0,
  area: 0,
  house_type: '',
  floor: '',
  total_floors: 1,
  orientation: '',
  decoration: '精装',
  build_year: new Date().getFullYear(),
  longitude: null,
  latitude: null,
  description: ''
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  district: [{ required: true, message: '请选择区域', trigger: 'change' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  area: [{ required: true, message: '请输入面积', trigger: 'blur' }],
  house_type: [{ required: true, message: '请选择户型', trigger: 'change' }],
  floor: [{ required: true, message: '请输入楼层', trigger: 'blur' }],
  total_floors: [{ required: true, message: '请输入总楼层', trigger: 'blur' }],
  orientation: [{ required: true, message: '请选择朝向', trigger: 'change' }]
}

// 获取区域列表
async function fetchDistrictList() {
  try {
    const res = await getDistrictList()
    if (res.code === 200) {
      districtList.value = res.data || []
    }
  } catch (error) {
    console.error('获取区域列表失败:', error)
  }
}

async function fetchHouseList() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      my_houses: true
    }
    
    // 添加搜索参数
    if (searchForm.keyword) {
      params.search = searchForm.keyword
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    if (searchForm.house_type) {
      params.house_type = searchForm.house_type
    }
    
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

function handleSearch() {
  currentPage.value = 1  // 搜索时重置到第一页
  fetchHouseList()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.status = ''
  searchForm.house_type = ''
  currentPage.value = 1
  fetchHouseList()
}

function handleSizeChange(val) {
  pageSize.value = val
  fetchHouseList()
}

function handleCurrentChange(val) {
  currentPage.value = val
  fetchHouseList()
}

async function handleStatusChange(row) {
  try {
    const res = await patchHouse(row.id, {
      status: row.status
    })
    if (res.code === 200) {
      ElMessage.success('状态更新成功')
      // 不需要重新加载整个列表，状态已经在row中更新
    } else {
      ElMessage.error(res.msg || '状态更新失败')
      // 恢复原状态
      fetchHouseList()
    }
  } catch (error) {
    console.error('状态更新失败:', error)
    let errorMsg = '状态更新失败'
    if (error.response && error.response.data) {
      errorMsg = error.response.data.msg || error.response.data.detail || errorMsg
    }
    ElMessage.error(errorMsg)
    // 恢复原状态
    fetchHouseList()
  }
}

function handleEdit(row) {
  isEdit.value = true
  // 只复制表单中存在的字段，避免提交多余字段
  houseForm.id = row.id
  houseForm.title = row.title
  houseForm.district = row.district || null
  houseForm.address = row.address
  houseForm.price = row.price
  houseForm.unit_price = row.unit_price || 0
  houseForm.area = row.area
  houseForm.house_type = row.house_type
  houseForm.floor = row.floor || ''
  houseForm.total_floors = row.total_floors || 1
  houseForm.orientation = row.orientation || ''
  houseForm.decoration = row.decoration || '精装'
  houseForm.build_year = row.build_year || new Date().getFullYear()
  houseForm.longitude = row.longitude || null
  houseForm.latitude = row.latitude || null
  houseForm.description = row.description || ''
  showCreateDialog.value = true
}

// 处理位置确认
function handleLocationConfirm(location) {
  if (location) {
    houseForm.longitude = location.longitude
    houseForm.latitude = location.latitude
  }
  showLocationPicker.value = false
  ElMessage.success('位置已设置')
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除这个房源吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      console.log('删除房源ID:', row.id)
      const res = await deleteHouse(row.id)
      console.log('删除响应:', res)
      if (res.code === 200 || res.code === 204) {
        ElMessage.success('删除成功')
        fetchHouseList()
      } else {
        ElMessage.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除房源失败:', error)
      let errorMsg = '删除失败'
      if (error.response && error.response.data) {
        errorMsg = error.response.data.msg || error.response.data.detail || errorMsg
      }
      ElMessage.error(errorMsg)
    }
  }).catch(() => {})
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let res
        if (isEdit.value) {
          // 编辑时使用 PATCH 方法，只提交表单中的字段
          const updateData = {
            title: houseForm.title,
            district: houseForm.district,
            address: houseForm.address,
            price: houseForm.price,
            unit_price: houseForm.unit_price,
            area: houseForm.area,
            house_type: houseForm.house_type,
            floor: houseForm.floor,
            total_floors: houseForm.total_floors,
            orientation: houseForm.orientation,
            decoration: houseForm.decoration,
            build_year: houseForm.build_year,
            longitude: houseForm.longitude,
            latitude: houseForm.latitude,
            description: houseForm.description
          }
          res = await patchHouse(houseForm.id, updateData)
        } else {
          // 创建时提交所有字段
          res = await createHouse({
            title: houseForm.title,
            district: houseForm.district,
            address: houseForm.address,
            price: houseForm.price,
            unit_price: houseForm.unit_price,
            area: houseForm.area,
            house_type: houseForm.house_type,
            floor: houseForm.floor,
            total_floors: houseForm.total_floors,
            orientation: houseForm.orientation,
            decoration: houseForm.decoration,
            build_year: houseForm.build_year,
            longitude: houseForm.longitude,
            latitude: houseForm.latitude,
            description: houseForm.description
          })
        }
        
        if (res.code === 200 || res.code === 201) {
          ElMessage.success(isEdit.value ? '更新成功' : '发布成功')
          showCreateDialog.value = false
          fetchHouseList()
          resetForm()
        } else {
          ElMessage.error(res.msg || '操作失败')
        }
      } catch (error) {
        console.error('提交失败:', error)
        let errorMsg = '操作失败'
        if (error.response && error.response.data) {
          // 尝试获取详细错误信息
          const data = error.response.data
          if (typeof data === 'object') {
            // 如果是字段错误，显示第一个错误
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
  })
}

function resetForm() {
  isEdit.value = false
  Object.assign(houseForm, {
    id: null,
    title: '',
    district: null,
    address: '',
    price: 0,
    unit_price: 0,
    area: 0,
    house_type: '',
    floor: '',
    total_floors: 1,
    orientation: '',
    decoration: '精装',
    build_year: new Date().getFullYear(),
    longitude: null,
    latitude: null,
    description: ''
  })
}

// 价格计算相关函数
// 根据单价计算总价
function calculatePriceFromUnit() {
  if (houseForm.unit_price > 0 && houseForm.area > 0) {
    // 单价(元/㎡) * 面积(㎡) / 10000 = 总价(万元)
    const calculatedPrice = (houseForm.unit_price * houseForm.area) / 10000
    houseForm.price = Number(calculatedPrice.toFixed(2))
  }
}

// 根据总价计算单价
function calculateUnitPrice() {
  if (houseForm.price > 0 && houseForm.area > 0) {
    // 总价(万元) * 10000 / 面积(㎡) = 单价(元/㎡)
    const calculatedUnitPrice = (houseForm.price * 10000) / houseForm.area
    houseForm.unit_price = Number(calculatedUnitPrice.toFixed(2))
  }
}

// 面积改变时，根据已有的单价或总价重新计算
function calculatePrice() {
  if (houseForm.area > 0) {
    // 如果已经输入了单价，根据单价计算总价
    if (houseForm.unit_price > 0) {
      calculatePriceFromUnit()
    }
    // 如果已经输入了总价，根据总价计算单价
    else if (houseForm.price > 0) {
      calculateUnitPrice()
    }
  }
}

// 管理图片
async function handleManageImages(row) {
  currentHouse.value = row
  showImageDialog.value = true
  await fetchHouseImages(row.id)
}

// 获取房源图片列表
async function fetchHouseImages(houseId) {
  try {
    const res = await request({
      url: '/house-images/',
      method: 'get',
      params: { house_id: houseId }
    })
    if (res.code === 200 || res.data) {
      imageList.value = res.data || res.results || []
    }
  } catch (error) {
    console.error('获取图片列表失败:', error)
  }
}

// 上传前验证
function beforeUpload(file) {
  console.log('准备上传文件:', {
    name: file.name,
    type: file.type,
    size: file.size,
    houseId: currentHouse.value?.id
  })

  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  
  if (!currentHouse.value?.id) {
    ElMessage.error('房源ID不存在，无法上传图片')
    return false
  }
  
  return true
}

// 上传成功
function handleUploadSuccess(response, file) {
  console.log('上传成功响应:', response)
  console.log('上传的文件:', file)
  
  // 处理不同的响应格式
  if (response.code === 200 || response.code === 201 || response.data) {
    ElMessage.success('图片上传成功')
    fetchHouseImages(currentHouse.value.id)
  } else {
    ElMessage.warning('上传完成，但响应格式异常')
    fetchHouseImages(currentHouse.value.id)
  }
}

// 上传失败
function handleUploadError(error) {
  console.error('上传失败详情:', error)
  
  // 尝试从error中提取详细信息
  let errorMsg = '图片上传失败'
  
  if (error.response) {
    console.error('错误响应:', error.response)
    const { status, data } = error.response
    
    if (data && typeof data === 'object') {
      // 处理字段错误
      if (data.image) {
        errorMsg = `图片字段错误: ${Array.isArray(data.image) ? data.image.join(', ') : data.image}`
      } else if (data.msg) {
        errorMsg = data.msg
      } else if (data.detail) {
        errorMsg = data.detail
      } else {
        errorMsg = `上传失败 (${status}): ${JSON.stringify(data)}`
      }
    } else if (typeof data === 'string') {
      errorMsg = `上传失败: ${data}`
    }
  } else if (error.message) {
    errorMsg = error.message
  }
  
  ElMessage.error(errorMsg)
}

// 删除图片
function handleDeleteImage(image) {
  ElMessageBox.confirm('确定要删除这张图片吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({
        url: `/house-images/${image.id}/`,
        method: 'delete'
      })
      if (res.code === 200 || res.code === 204) {
        ElMessage.success('删除成功')
        fetchHouseImages(currentHouse.value.id)
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchDistrictList()
  fetchHouseList()
})
</script>

<style lang="scss" scoped>
.my-houses-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-section {
    margin-bottom: 20px;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 4px;

    .search-form {
      margin: 0;
    }
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

.form-tip {
  display: inline-block;
  margin-top: 4px;
  font-size: 12px;
  color: #67c23a;
  font-weight: 500;
}

.image-manager {
  .image-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;

    .image-item {
      position: relative;
      border: 1px solid #dcdfe6;
      border-radius: 6px;
      overflow: hidden;

      &:hover .image-actions {
        opacity: 1;
      }

      .image-actions {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(0, 0, 0, 0.7);
        padding: 8px;
        display: flex;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s;
      }
    }
  }
}
</style>

