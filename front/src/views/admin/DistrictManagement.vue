<template>
  <div class="district-management">
    <div class="page-header">
      <h2>区域管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增区域
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="城市">
          <el-input v-model="searchForm.city" placeholder="请输入城市名称" clearable />
        </el-form-item>
        <el-form-item label="区域名称">
          <el-input v-model="searchForm.name" placeholder="请输入区域名称" clearable />
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
    </el-card>

    <!-- 区域列表 -->
    <el-card class="table-card">
      <el-table 
        :data="districtList" 
        v-loading="loading"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="区域名称" min-width="120" />
        <el-table-column prop="city" label="城市" min-width="100" />
        <el-table-column prop="description" label="区域描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="house_count" label="房源数量" width="100" align="center">
          <template #default="{ row }">
            <el-tag>{{ row.house_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              link
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑区域对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="区域名称" prop="name">
          <el-input 
            v-model="formData.name" 
            placeholder="请输入区域名称"
            :disabled="dialogMode === 'view'"
          />
        </el-form-item>
        <el-form-item label="城市" prop="city">
          <el-input 
            v-model="formData.city" 
            placeholder="请输入城市名称"
            :disabled="dialogMode === 'view'"
          />
        </el-form-item>
        <el-form-item label="区域描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入区域描述"
            :disabled="dialogMode === 'view'"
          />
        </el-form-item>
      </el-form>

      <template #footer v-if="dialogMode !== 'view'">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
      <template #footer v-else>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getDistrictList, 
  getDistrictDetail,
  createDistrict, 
  updateDistrict, 
  deleteDistrict 
} from '@/api/house'

// 搜索表单
const searchForm = reactive({
  city: '',
  name: ''
})

// 区域列表数据
const districtList = ref([])
const loading = ref(false)

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogMode = ref('add') // add, edit, view
const formRef = ref(null)
const submitting = ref(false)

// 表单数据
const formData = reactive({
  id: null,
  name: '',
  city: '上海',
  description: ''
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入区域名称', trigger: 'blur' },
    { min: 2, max: 50, message: '区域名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  city: [
    { required: true, message: '请输入城市名称', trigger: 'blur' },
    { min: 2, max: 50, message: '城市名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 获取区域列表
async function fetchDistrictList() {
  loading.value = true
  try {
    const params = {}
    if (searchForm.city) params.city = searchForm.city
    if (searchForm.name) params.name = searchForm.name

    const res = await getDistrictList(params)
    if (res.code === 200) {
      districtList.value = res.data
    } else {
      ElMessage.error(res.msg || '获取区域列表失败')
    }
  } catch (error) {
    console.error('获取区域列表失败:', error)
    ElMessage.error(error.response?.data?.msg || '获取区域列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  fetchDistrictList()
}

// 重置搜索
function handleReset() {
  searchForm.city = ''
  searchForm.name = ''
  fetchDistrictList()
}

// 新增区域
function handleAdd() {
  dialogMode.value = 'add'
  dialogTitle.value = '新增区域'
  resetFormData()
  dialogVisible.value = true
}

// 查看区域
async function handleView(row) {
  dialogMode.value = 'view'
  dialogTitle.value = '查看区域'
  try {
    const res = await getDistrictDetail(row.id)
    if (res.code === 200) {
      Object.assign(formData, res.data)
      dialogVisible.value = true
    } else {
      ElMessage.error(res.msg || '获取区域详情失败')
    }
  } catch (error) {
    console.error('获取区域详情失败:', error)
    ElMessage.error(error.response?.data?.msg || '获取区域详情失败')
  }
}

// 编辑区域
async function handleEdit(row) {
  dialogMode.value = 'edit'
  dialogTitle.value = '编辑区域'
  try {
    const res = await getDistrictDetail(row.id)
    if (res.code === 200) {
      Object.assign(formData, res.data)
      dialogVisible.value = true
    } else {
      ElMessage.error(res.msg || '获取区域详情失败')
    }
  } catch (error) {
    console.error('获取区域详情失败:', error)
    ElMessage.error(error.response?.data?.msg || '获取区域详情失败')
  }
}

// 删除区域
function handleDelete(row) {
  ElMessageBox.confirm(
    `确定要删除区域 "${row.name}" 吗？该操作不可恢复！`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await deleteDistrict(row.id)
      if (res.code === 200 || res.code === 204) {
        ElMessage.success('删除成功')
        fetchDistrictList()
      } else {
        ElMessage.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除区域失败:', error)
      ElMessage.error(error.response?.data?.msg || '删除失败')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const data = {
        name: formData.name,
        city: formData.city,
        description: formData.description
      }
      
      let res
      if (dialogMode.value === 'add') {
        res = await createDistrict(data)
      } else {
        res = await updateDistrict(formData.id, data)
      }
      
      if (res.code === 200 || res.code === 201) {
        ElMessage.success(dialogMode.value === 'add' ? '创建成功' : '更新成功')
        dialogVisible.value = false
        fetchDistrictList()
      } else {
        ElMessage.error(res.msg || '操作失败')
      }
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error(error.response?.data?.msg || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单数据
function resetFormData() {
  formData.id = null
  formData.name = ''
  formData.city = '上海'
  formData.description = ''
}

// 对话框关闭
function handleDialogClose() {
  formRef.value?.resetFields()
  resetFormData()
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 页面加载时获取数据
onMounted(() => {
  fetchDistrictList()
})
</script>

<style lang="scss" scoped>
.district-management {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
  }

  .search-card {
    margin-bottom: 20px;
  }

  .table-card {
    :deep(.el-card__body) {
      padding: 0;
    }

    .el-table {
      :deep(.el-button.is-link) {
        padding: 0 4px;
      }
    }
  }
}
</style>

