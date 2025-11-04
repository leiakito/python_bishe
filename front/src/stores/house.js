import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useHouseStore = defineStore('house', () => {
  // 搜索条件
  const searchParams = ref({
    search: '',
    district: '',
    house_type: '',
    min_price: '',
    max_price: '',
    min_area: '',
    max_area: '',
    status: 'available',
    ordering: '-created_at'
  })

  // 房源列表
  const houseList = ref([])
  
  // 当前房源详情
  const currentHouse = ref(null)

  /**
   * 更新搜索条件
   */
  function updateSearchParams(params) {
    searchParams.value = { ...searchParams.value, ...params }
  }

  /**
   * 重置搜索条件
   */
  function resetSearchParams() {
    searchParams.value = {
      search: '',
      district: '',
      house_type: '',
      min_price: '',
      max_price: '',
      min_area: '',
      max_area: '',
      status: 'available',
      ordering: '-created_at'
    }
  }

  /**
   * 设置房源列表
   */
  function setHouseList(list) {
    houseList.value = list
  }

  /**
   * 设置当前房源
   */
  function setCurrentHouse(house) {
    currentHouse.value = house
  }

  return {
    searchParams,
    houseList,
    currentHouse,
    updateSearchParams,
    resetSearchParams,
    setHouseList,
    setCurrentHouse
  }
})

