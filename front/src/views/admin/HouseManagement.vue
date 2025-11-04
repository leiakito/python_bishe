<template>
  <div class="house-management">
    <div class="page-title">房源管理</div>

    <!-- 筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="标题/地址"
            clearable
            style="width: 200px"
            @keyup.enter="fetchHouses"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="全部"
            clearable
            style="width: 120px"
            @change="fetchHouses"
          >
            <el-option label="在售" value="available" />
            <el-option label="已售" value="sold" />
            <el-option label="已租" value="rented" />
            <el-option label="待定" value="pending" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="fetchHouses">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 房源列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>房源列表</span>
          <div>
            <el-button
              type="warning"
              :disabled="selectedIds.length === 0"
              @click="showBatchStatusDialog"
            >
              <el-icon><Edit /></el-icon>
              批量更新状态
            </el-button>
            <el-button
              type="danger"
              :disabled="selectedIds.length === 0"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="houseList"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" width="200" show-overflow-tooltip />
        <el-table-column prop="district_name" label="区域" width="100" />
        <el-table-column prop="price" label="价格(万)" width="100" />
        <el-table-column prop="area" label="面积(㎡)" width="100" />
        <el-table-column prop="house_type" label="户型" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="agent_name" label="经纪人" width="120" />
        <el-table-column prop="views" label="浏览" width="80" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="scope">
            <el-button
              link
              type="primary"
              size="small"
              @click="handleView(scope.row)"
            >
              查看
            </el-button>
            <el-button
              link
              type="warning"
              size="small"
              @click="handleEditStatus(scope.row)"
            >
              状态
            </el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchHouses"
        @current-change="fetchHouses"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <!-- 批量更新状态对话框 -->
    <el-dialog
      v-model="batchStatusDialogVisible"
      title="批量更新状态"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="新状态">
          <el-select v-model="batchStatus" style="width: 100%">
            <el-option label="在售" value="available" />
            <el-option label="已售" value="sold" />
            <el-option label="已租" value="rented" />
            <el-option label="待定" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-alert
            :title="`将更新 ${selectedIds.length} 个房源的状态`"
            type="info"
            :closable="false"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="batchStatusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchUpdateStatus">确定</el-button>
      </template>
    </el-dialog>

    <!-- 单个房源状态更新对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      title="更新房源状态"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="房源">
          <el-text>{{ currentHouse?.title }}</el-text>
        </el-form-item>
        <el-form-item label="新状态">
          <el-select v-model="newStatus" style="width: 100%">
            <el-option label="在售" value="available" />
            <el-option label="已售" value="sold" />
            <el-option label="已租" value="rented" />
            <el-option label="待定" value="pending" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateStatus">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const houseList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedIds = ref([])

const filterForm = reactive({
  search: '',
  status: ''
})

const batchStatusDialogVisible = ref(false)
const batchStatus = ref('available')

const statusDialogVisible = ref(false)
const currentHouse = ref(null)
const newStatus = ref('available')

async function fetchHouses() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (filterForm.search) params.search = filterForm.search
    if (filterForm.status) params.status = filterForm.status

    const res = await request({
      url: '/houses/',
      method: 'get',
      params
    })

    if (res.code === 200) {
      houseList.value = res.data.results || []
      total.value = res.data.count || 0
    }
  } catch (error) {
    console.error('获取房源列表失败:', error)
    ElMessage.error('获取房源列表失败')
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  filterForm.search = ''
  filterForm.status = ''
  currentPage.value = 1
  fetchHouses()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.id)
}

function showBatchStatusDialog() {
  batchStatus.value = 'available'
  batchStatusDialogVisible.value = true
}

async function handleBatchUpdateStatus() {
  try {
    const res = await request({
      url: '/houses/batch_update_status/',
      method: 'post',
      data: {
        ids: selectedIds.value,
        status: batchStatus.value
      }
    })

    if (res.code === 200) {
      ElMessage.success(res.msg || '批量更新成功')
      batchStatusDialogVisible.value = false
      fetchHouses()
    }
  } catch (error) {
    console.error('批量更新失败:', error)
    ElMessage.error(error.response?.data?.msg || '批量更新失败')
  }
}

function handleBatchDelete() {
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedIds.value.length} 个房源吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await request({
        url: '/houses/batch_delete/',
        method: 'post',
        data: {
          ids: selectedIds.value
        }
      })

      if (res.code === 200) {
        ElMessage.success(res.msg || '批量删除成功')
        fetchHouses()
      }
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error(error.response?.data?.msg || '批量删除失败')
    }
  }).catch(() => {})
}

function handleView(row) {
  router.push(`/houses/${row.id}`)
}

function handleEditStatus(row) {
  currentHouse.value = row
  newStatus.value = row.status
  statusDialogVisible.value = true
}

async function handleUpdateStatus() {
  try {
    const res = await request({
      url: `/houses/${currentHouse.value.id}/`,
      method: 'patch',
      data: {
        status: newStatus.value
      }
    })

    if (res.code === 200) {
      ElMessage.success('更新成功')
      statusDialogVisible.value = false
      fetchHouses()
    }
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error(error.response?.data?.msg || '更新失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(
    `确定要删除房源 "${row.title}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await request({
        url: `/houses/${row.id}/`,
        method: 'delete'
      })

      if (res.code === 204 || res.code === 200) {
        ElMessage.success('删除成功')
        fetchHouses()
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.msg || '删除失败')
    }
  }).catch(() => {})
}

function getStatusType(status) {
  const map = {
    'available': 'success',
    'sold': 'info',
    'rented': 'warning',
    'pending': 'danger'
  }
  return map[status] || ''
}

function getStatusText(status) {
  const map = {
    'available': '在售',
    'sold': '已售',
    'rented': '已租',
    'pending': '待定'
  }
  return map[status] || status
}

onMounted(() => {
  fetchHouses()
})
</script>

<style lang="scss" scoped>
.house-management {
  .filter-card {
    margin-bottom: 20px;
  }

  .table-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      span {
        font-weight: bold;
        font-size: 16px;
      }
    }
  }
}
</style>

