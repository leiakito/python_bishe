<template>
  <el-card class="house-card" :body-style="{ padding: '0' }" shadow="hover">
    <div class="house-image" @click="handleClick">
      <img :src="house.cover_image || '/default-house.jpg'" :alt="house.title" />
      <el-tag class="status-tag" :type="getHouseStatusType(house.status)">
        {{ getHouseStatusText(house.status) }}
      </el-tag>
    </div>
    <div class="house-info">
      <h3 class="house-title" @click="handleClick">
        {{ house.title }}
      </h3>
      <p class="house-address">
        <el-icon><Location /></el-icon>
        {{ house.address }}
      </p>
      <div class="house-details">
        <span>{{ house.house_type }}</span>
        <span>{{ house.area }}㎡</span>
        <span v-if="house.floor && house.total_floors">
          {{ house.floor }}/{{ house.total_floors }}层
        </span>
      </div>
      <div class="house-footer">
        <div class="house-price">
          <span class="price">{{ formatPrice(house.price) }}</span>
          <span class="unit">万</span>
        </div>
        <slot name="actions"></slot>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { formatPrice, getHouseStatusText, getHouseStatusType } from '@/utils'

defineProps({
  house: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])

function handleClick() {
  emit('click')
}
</script>

<style lang="scss" scoped>
.house-card {
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
  }
}
</style>

