<template>
  <div class="user-management">
    <div class="page-title">用户管理</div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="用户名/手机/姓名"
            clearable
            style="width: 200px"
            @keyup.enter="fetchUsers"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="角色">
          <el-select
            v-model="filterForm.role"
            placeholder="全部"
            clearable
            style="width: 120px"
            @change="fetchUsers"
          >
            <el-option label="普通用户" value="user" />
            <el-option label="经纪人" value="agent" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="filterForm.is_active"
            placeholder="全部"
            clearable
            style="width: 120px"
            @change="fetchUsers"
          >
            <el-option label="激活" value="true" />
            <el-option label="禁用" value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="fetchUsers">
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

    <!-- 用户列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>

      <el-table
        :data="userList"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="scope">
            <el-tag :type="getRoleType(scope.row.role)">
              {{ getRoleText(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_verified" label="认证" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_verified ? 'success' : 'info'">
              {{ scope.row.is_verified ? '已认证' : '未认证' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="scope">
            <el-button
              link
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-tooltip
              :content="scope.row.is_superuser ? '超级管理员不能删除' : '删除用户'"
              placement="top"
            >
              <el-button
                link
                type="danger"
                size="small"
                @click="handleDelete(scope.row)"
                :disabled="cannotDelete(scope.row)"
              >
                删除
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchUsers"
        @current-change="fetchUsers"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="userForm.real_name" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="经纪人" value="agent" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="公司" prop="company">
          <el-input v-model="userForm.company" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
        <el-form-item label="认证状态" prop="is_verified">
          <el-switch v-model="userForm.is_verified" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDate } from '@/utils'

const loading = ref(false)
const submitLoading = ref(false)
const userList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filterForm = reactive({
  search: '',
  role: '',
  is_active: ''
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增用户')
const isEdit = ref(false)
const userFormRef = ref(null)

const userForm = reactive({
  id: null,
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
  role: 'user',
  company: '',
  is_active: true,
  is_verified: false
})

const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

async function fetchUsers() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (filterForm.search) params.search = filterForm.search
    if (filterForm.role) params.role = filterForm.role
    if (filterForm.is_active) params.is_active = filterForm.is_active

    console.log('请求参数:', params)
    const res = await request({
      url: '/users/',
      method: 'get',
      params
    })

    console.log('API响应:', res)
    console.log('res.data:', res.data)
    console.log('res.data.results:', res.data?.results)
    console.log('res.data.count:', res.data?.count)

    if (res.code === 200) {
      // 处理可能的数据嵌套
      if (res.data && typeof res.data === 'object') {
        // 如果data里有results，说明是分页数据
        if (res.data.results !== undefined) {
          userList.value = res.data.results || []
          total.value = res.data.count || 0
        } else if (Array.isArray(res.data)) {
          // 如果data本身就是数组
          userList.value = res.data
          total.value = res.data.length
        } else {
          console.warn('未知的数据格式:', res.data)
          userList.value = []
          total.value = 0
        }
      } else {
        userList.value = []
        total.value = 0
      }
      console.log('设置后的userList:', userList.value)
      console.log('设置后的total:', total.value)
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error(error.response?.data?.msg || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  filterForm.search = ''
  filterForm.role = ''
  filterForm.is_active = ''
  currentPage.value = 1
  fetchUsers()
}

function showCreateDialog() {
  isEdit.value = false
  dialogTitle.value = '新增用户'
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    real_name: row.real_name || '',
    phone: row.phone,
    email: row.email || '',
    role: row.role,
    company: row.company || '',
    is_active: row.is_active,
    is_verified: row.is_verified
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await userFormRef.value.validate()
    submitLoading.value = true

    const data = {
      username: userForm.username,
      real_name: userForm.real_name,
      phone: userForm.phone,
      email: userForm.email,
      role: userForm.role,
      company: userForm.company,
      is_active: userForm.is_active,
      is_verified: userForm.is_verified
    }

    if (!isEdit.value) {
      data.password = userForm.password
    }

    const res = await request({
      url: isEdit.value ? `/users/${userForm.id}/` : '/users/',
      method: isEdit.value ? 'put' : 'post',
      data
    })

    if (res.code === 200 || res.code === 201) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      fetchUsers()
    }
  } catch (error) {
    console.error('提交失败:', error)
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (typeof errorData === 'object') {
        const firstError = Object.values(errorData)[0]
        ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
      }
    } else {
      ElMessage.error('操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

function handleDelete(row) {
  // 前端二次确认：如果是超级管理员，不允许删除
  if (row.is_superuser) {
    ElMessage.warning('超级管理员不能删除')
    return
  }
  
  const roleText = getRoleText(row.role)
  ElMessageBox.confirm(
    `确定要删除${roleText} "${row.username}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: false
    }
  ).then(async () => {
    try {
      const res = await request({
        url: `/users/${row.id}/`,
        method: 'delete'
      })

      if (res.code === 204 || res.code === 200) {
        ElMessage.success(`${roleText} "${row.username}" 删除成功`)
        fetchUsers()
      } else {
        ElMessage.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      const errorMsg = error.response?.data?.msg || error.response?.data?.detail || '删除失败'
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消删除，不需要提示
  })
}

function resetForm() {
  userForm.id = null
  userForm.username = ''
  userForm.password = ''
  userForm.real_name = ''
  userForm.phone = ''
  userForm.email = ''
  userForm.role = 'user'
  userForm.company = ''
  userForm.is_active = true
  userForm.is_verified = false
}

function getRoleType(role) {
  const map = {
    'user': '',
    'agent': 'success',
    'admin': 'danger'
  }
  return map[role] || ''
}

function getRoleText(role) {
  const map = {
    'user': '普通用户',
    'agent': '经纪人',
    'admin': '管理员'
  }
  return map[role] || role
}

// 判断是否不能删除该用户
function cannotDelete(row) {
  // 只有超级管理员不能被删除
  // 普通用户(user)、经纪人(agent)和普通管理员(admin但非superuser)都可以删除
  const cannot = row.is_superuser === true
  return cannot
}

onMounted(() => {
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.user-management {
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

