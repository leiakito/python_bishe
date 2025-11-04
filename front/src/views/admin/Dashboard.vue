<template>
  <div class="admin-dashboard">
    <div class="page-title">管理中心</div>

    <!-- 快捷入口 -->
    <el-row :gutter="20" class="quick-links">
      <el-col :span="6">
        <el-card shadow="hover" class="quick-link-card" @click="$router.push('/admin/users')">
          <div class="card-content">
            <el-icon :size="48" color="#409eff"><User /></el-icon>
            <h3>用户管理</h3>
            <p>管理系统用户，包括角色分配</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="quick-link-card" @click="$router.push('/admin/houses')">
          <div class="card-content">
            <el-icon :size="48" color="#67c23a"><House /></el-icon>
            <h3>房源管理</h3>
            <p>统一管理系统房源信息</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="quick-link-card" @click="$router.push('/admin/districts')">
          <div class="card-content">
            <el-icon :size="48" color="#f56c6c"><Location /></el-icon>
            <h3>区域管理</h3>
            <p>管理城市区域信息</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="quick-link-card" @click="$router.push('/analysis')">
          <div class="card-content">
            <el-icon :size="48" color="#e6a23c"><TrendCharts /></el-icon>
            <h3>数据分析</h3>
            <p>查看系统数据统计分析</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计数据 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card>
          <el-statistic title="总用户数" :value="stats.total_users">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <el-statistic title="总房源数" :value="stats.total_houses">
            <template #prefix>
              <el-icon><House /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <el-statistic title="在售房源" :value="stats.available_houses">
            <template #prefix>
              <el-icon><Sell /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <el-statistic title="平均价格" :value="stats.avg_price" suffix="万元" :precision="2">
            <template #prefix>
              <el-icon><Money /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新活动 -->
    <el-card class="activity-card">
      <template #header>
        <div class="card-header">
          <span>系统概览</span>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="普通用户">
          {{ stats.user_count }} 人
        </el-descriptions-item>
        <el-descriptions-item label="经纪人">
          {{ stats.agent_count }} 人
        </el-descriptions-item>
        <el-descriptions-item label="已售房源">
          {{ stats.sold_houses }} 套
        </el-descriptions-item>
        <el-descriptions-item label="已租房源">
          {{ stats.rented_houses }} 套
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <div class="action-buttons">
        <el-button type="primary" @click="$router.push('/admin/users')">
          <el-icon><User /></el-icon>
          管理用户
        </el-button>
        <el-button type="success" @click="$router.push('/admin/houses')">
          <el-icon><House /></el-icon>
          管理房源
        </el-button>
        <el-button type="danger" @click="$router.push('/admin/districts')">
          <el-icon><Location /></el-icon>
          管理区域
        </el-button>
        <el-button type="info" @click="fetchStats">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const stats = ref({
  total_users: 0,
  user_count: 0,
  agent_count: 0,
  total_houses: 0,
  available_houses: 0,
  sold_houses: 0,
  rented_houses: 0,
  avg_price: 0
})

async function fetchStats() {
  try {
    // 获取用户统计
    const userRes = await request({
      url: '/users/',
      method: 'get',
      params: { page_size: 1 }
    })
    
    console.log('用户统计响应:', userRes)
    if (userRes.code === 200) {
      // 处理可能的数据嵌套
      const count = userRes.data?.count || userRes.data?.data?.count || 0
      stats.value.total_users = count
    }

    // 获取房源统计
    const houseRes = await request({
      url: '/houses/stats/',
      method: 'get'
    })

    console.log('房源统计响应:', houseRes)
    if (houseRes.code === 200) {
      const data = houseRes.data
      stats.value.total_houses = data.total_houses || 0
      stats.value.avg_price = data.avg_price || 0

      // 统计各状态房源
      if (data.status_stats && Array.isArray(data.status_stats)) {
        data.status_stats.forEach(item => {
          if (item.status === 'available') {
            stats.value.available_houses = item.count
          } else if (item.status === 'sold') {
            stats.value.sold_houses = item.count
          } else if (item.status === 'rented') {
            stats.value.rented_houses = item.count
          }
        })
      }
    }

    // 获取角色统计
    const userRoleRes = await request({
      url: '/users/',
      method: 'get',
      params: { role: 'user', page_size: 1 }
    })
    if (userRoleRes.code === 200) {
      const count = userRoleRes.data?.count || userRoleRes.data?.data?.count || 0
      stats.value.user_count = count
    }

    const agentRoleRes = await request({
      url: '/users/',
      method: 'get',
      params: { role: 'agent', page_size: 1 }
    })
    if (agentRoleRes.code === 200) {
      const count = agentRoleRes.data?.count || agentRoleRes.data?.data?.count || 0
      stats.value.agent_count = count
    }

  } catch (error) {
    console.error('获取统计数据失败:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error(error.response?.data?.msg || '获取统计数据失败')
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style lang="scss" scoped>
.admin-dashboard {
  .quick-links {
    margin-bottom: 20px;

    .quick-link-card {
      cursor: pointer;
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-5px);
      }

      .card-content {
        text-align: center;
        padding: 20px;

        h3 {
          margin: 15px 0 10px;
          font-size: 18px;
          color: #303133;
        }

        p {
          margin: 0;
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .stats-cards {
    margin-bottom: 20px;
  }

  .activity-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      span {
        font-weight: bold;
        font-size: 16px;
      }
    }

    .action-buttons {
      margin-top: 20px;
      display: flex;
      gap: 10px;
    }
  }
}
</style>

