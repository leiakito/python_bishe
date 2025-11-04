<template>
  <div class="price-alerts-page">
    <div class="page-title">价格提醒</div>

    <el-card>
      <el-table :data="alertList" v-loading="loading" stripe>
        <el-table-column prop="house.title" label="房源" min-width="200">
          <template #default="{ row }">
            <el-link
              type="primary"
              @click="$router.push(`/houses/${row.house.id}`)"
            >
              {{ row.house.title }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column prop="house.address" label="地址" min-width="150" />

        <el-table-column label="当前价格" width="120">
          <template #default="{ row }">
            <span class="price">{{ formatPrice(row.current_price) }}万</span>
          </template>
        </el-table-column>

        <el-table-column label="目标价格" width="120">
          <template #default="{ row }">
            <span class="price">{{ formatPrice(row.target_price) }}万</span>
          </template>
        </el-table-column>

        <el-table-column label="差价" width="120">
          <template #default="{ row }">
            <el-tag
              :type="row.current_price <= row.target_price ? 'success' : 'info'"
            >
              {{ (row.current_price - row.target_price).toFixed(2) }}万
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getAlertStatusType(row.status)">
              {{ getAlertStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="触发时间" width="180">
          <template #default="{ row }">
            {{ row.triggered_at ? formatDate(row.triggered_at) : '-' }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'active'"
              type="warning"
              size="small"
              @click="handleCancel(row)"
            >
              取消
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

      <el-empty v-if="!loading && alertList.length === 0" description="暂无价格提醒" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPriceAlertList, cancelPriceAlert, deletePriceAlert } from '@/api/favorite'
import { formatPrice, formatDate, getAlertStatusText, getAlertStatusType } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const alertList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function fetchAlertList() {
  loading.value = true
  try {
    const res = await getPriceAlertList({
      page: currentPage.value,
      page_size: pageSize.value
    })
    if (res.code === 200) {
      alertList.value = res.data.results || []
      total.value = res.data.count || 0
    }
  } catch (error) {
    console.error('获取价格提醒列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSizeChange(val) {
  pageSize.value = val
  fetchAlertList()
}

function handleCurrentChange(val) {
  currentPage.value = val
  fetchAlertList()
}

function handleCancel(row) {
  ElMessageBox.confirm('确定要取消这个价格提醒吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await cancelPriceAlert(row.id)
      if (res.code === 200) {
        ElMessage.success('已取消提醒')
        fetchAlertList()
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除这个价格提醒吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deletePriceAlert(row.id)
      if (res.code === 200 || res.code === 204) {
        ElMessage.success('删除成功')
        fetchAlertList()
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchAlertList()
})
</script>

<style lang="scss" scoped>
.price-alerts-page {
  .price {
    color: #f56c6c;
    font-weight: bold;
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}
</style>

