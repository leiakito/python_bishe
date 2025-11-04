<template>
  <div class="profile-page">
    <div class="page-title">个人中心</div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="user-card">
          <div class="user-avatar">
            <el-avatar :size="100">
              <el-icon :size="50"><User /></el-icon>
            </el-avatar>
          </div>
          <div class="user-info">
            <h3>{{ userStore.userInfo?.username }}</h3>
            <el-tag :type="getRoleType(userStore.userInfo?.role)">
              {{ getUserRoleText(userStore.userInfo?.role) }}
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-button
                v-if="!isEditing"
                type="primary"
                size="small"
                @click="isEditing = true"
              >
                编辑
              </el-button>
              <div v-else>
                <el-button size="small" @click="cancelEdit">取消</el-button>
                <el-button type="primary" size="small" @click="handleSave">
                  保存
                </el-button>
              </div>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="profileForm"
            :rules="rules"
            label-width="100px"
            :disabled="!isEditing"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>

            <el-form-item label="真实姓名" prop="real_name">
              <el-input v-model="profileForm.real_name" />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>

            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" />
            </el-form-item>

            <el-form-item label="公司" prop="company" v-if="isAgent">
              <el-input v-model="profileForm.company" />
            </el-form-item>
          </el-form>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>修改密码</span>
          </template>

          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="原密码" prop="old_password">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                show-password
              />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                show-password
              />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleChangePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { updateUserProfile, changePassword } from '@/api/user'
import { getUserRoleText } from '@/utils'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const formRef = ref(null)
const passwordFormRef = ref(null)
const isEditing = ref(false)

const profileForm = reactive({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  company: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const isAgent = computed(() => {
  return userStore.userInfo?.role === 'agent'
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const validateNewPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入新密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度至少6位'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, validator: validateNewPassword, trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

function getRoleType(role) {
  const typeMap = {
    user: 'info',
    agent: 'success',
    admin: 'danger'
  }
  return typeMap[role] || 'info'
}

function loadUserInfo() {
  const userInfo = userStore.userInfo
  if (userInfo) {
    Object.assign(profileForm, {
      username: userInfo.username,
      real_name: userInfo.real_name || '',
      email: userInfo.email || '',
      phone: userInfo.phone || '',
      company: userInfo.company || ''
    })
  }
}

function cancelEdit() {
  isEditing.value = false
  loadUserInfo()
}

async function handleSave() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const { username, ...data } = profileForm
        const res = await updateUserProfile(data)
        if (res.code === 200) {
          userStore.updateUserInfo(res.data)
          ElMessage.success('保存成功')
          isEditing.value = false
        }
      } catch (error) {
        ElMessage.error('保存失败')
      }
    }
  })
}

async function handleChangePassword() {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const res = await changePassword(passwordForm)
        if (res.code === 200) {
          ElMessage.success('密码修改成功，请重新登录')
          passwordForm.old_password = ''
          passwordForm.new_password = ''
          passwordForm.confirm_password = ''
          // 退出登录
          setTimeout(() => {
            userStore.logout()
            window.location.href = '/login'
          }, 1500)
        }
      } catch (error) {
        ElMessage.error('密码修改失败')
      }
    }
  })
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style lang="scss" scoped>
.profile-page {
  .user-card {
    text-align: center;

    .user-avatar {
      margin-bottom: 20px;
    }

    .user-info {
      h3 {
        margin: 10px 0;
        font-size: 20px;
        color: #303133;
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>

