<template>
  <div class="favorites-page">
    <div class="page-title">我的收藏</div>

    <div class="favorites-list" v-loading="loading">
      <el-row :gutter="20">
        <el-col
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          v-for="item in favoriteList"
          :key="item.id"
        >
          <el-card class="favorite-card" :body-style="{ padding: '0' }" shadow="hover">
            <div class="house-image" @click="goToDetail(item.house.id)">
              <img
                :src="item.house.cover_image || '/default-house.jpg'"
                :alt="item.house.title"
              />
              <el-tag class="status-tag" :type="getHouseStatusType(item.house.status)">
                {{ getHouseStatusText(item.house.status) }}
              </el-tag>
            </div>
            <div class="house-info">
              <h3 class="house-title" @click="goToDetail(item.house.id)">
                {{ item.house.title }}
              </h3>
              <p class="house-address">
                <el-icon><Location /></el-icon>
                {{ item.house.address }}
              </p>
              <div class="house-details">
                <span>{{ item.house.house_type }}</span>
                <span>{{ item.house.area }}㎡</span>
              </div>
              <div class="house-footer">
                <div class="house-price">
                  <span class="price">{{ formatPrice(item.house.price) }}</span>
                  <span class="unit">万</span>
                </div>
                <el-button
                  type="danger"
                  icon="Delete"
                  circle
                  size="small"
                  @click="handleRemove(item)"
                />
              </div>
              <div class="favorite-note" v-if="item.note">
                <el-text type="info" size="small">备注: {{ item.note }}</el-text>
              </div>
              <div class="favorite-time">
                <el-text type="info" size="small">
                  收藏于 {{ formatDate(item.created_at, 'YYYY-MM-DD') }}
                </el-text>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && favoriteList.length === 0" description="暂无收藏" />

      <!-- 分页 -->
      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 36, 48]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFavoriteList, removeFavorite } from '@/api/favorite'
import { formatPrice, formatDate, getHouseStatusText, getHouseStatusType } from '@/utils'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const favoriteList = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

async function fetchFavoriteList() {
  loading.value = true
  try {
    const res = await getFavoriteList({
      page: currentPage.value,
      page_size: pageSize.value
    })
    console.log('收藏列表API响应:', res)
    if (res.code === 200) {
      favoriteList.value = res.data.results || []
      total.value = res.data.count || 0
      console.log('收藏列表数据:', favoriteList.value)
      if (favoriteList.value.length > 0) {
        console.log('第一个收藏项:', favoriteList.value[0])
        console.log('第一个房源封面图:', favoriteList.value[0].house?.cover_image)
      }
    }
  } catch (error) {
    console.error('获取收藏列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSizeChange(val) {
  pageSize.value = val
  fetchFavoriteList()
}

function handleCurrentChange(val) {
  currentPage.value = val
  fetchFavoriteList()
}

function goToDetail(id) {
  router.push(`/houses/${id}`)
}

function handleRemove(item) {
  ElMessageBox.confirm('确定要取消收藏吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await removeFavorite(item.id)
      if (res.code === 200 || res.code === 204) {
        ElMessage.success('已取消收藏')
        fetchFavoriteList()
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchFavoriteList()
})
</script>

<style lang="scss" scoped>
.favorites-page {
  .favorites-list {
    .favorite-card {
      margin-bottom: 20px;
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-5px);
      }

      .house-image {
        position: relative;
        height: 200px;
        overflow: hidden;
        cursor: pointer;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.3s;
        }

        &:hover img {
          transform: scale(1.1);
        }

        .status-tag {
          position: absolute;
          top: 10px;
          right: 10px;
        }
      }

      .house-info {
        padding: 15px;

        .house-title {
          font-size: 16px;
          color: #303133;
          margin-bottom: 8px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          cursor: pointer;

          &:hover {
            color: #409eff;
          }
        }

        .house-address {
          font-size: 14px;
          color: #909399;
          margin-bottom: 10px;
          display: flex;
          align-items: center;
          gap: 4px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .house-details {
          display: flex;
          gap: 10px;
          margin-bottom: 10px;
          font-size: 14px;
          color: #606266;

          span {
            padding: 2px 8px;
            background: #f5f7fa;
            border-radius: 4px;
            font-size: 12px;
          }
        }

        .house-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;

          .house-price {
            .price {
              font-size: 24px;
              color: #f56c6c;
              font-weight: bold;
            }

            .unit {
              font-size: 14px;
              color: #f56c6c;
              margin-left: 2px;
            }
          }
        }

        .favorite-note {
          margin-bottom: 5px;
          padding: 5px;
          background: #f5f7fa;
          border-radius: 4px;
        }

        .favorite-time {
          text-align: right;
        }
      }
    }

    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 30px;
    }
  }
}
</style>

