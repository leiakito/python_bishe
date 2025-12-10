<template>
  <div class="analysis-page">
    <div class="page-title">数据分析</div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="区域">
          <el-select
            v-model="filterForm.district"
            placeholder="选择区域"
            clearable
            style="width: 150px"
            @change="fetchAllData"
          >
            <el-option
              v-for="district in districts"
              :key="district.id"
              :label="district.name"
              :value="district.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-select
            v-model="filterForm.months"
            placeholder="选择月份"
            style="width: 120px"
            @change="fetchPriceTrend"
          >
            <el-option label="近3个月" :value="3" />
            <el-option label="近6个月" :value="6" />
            <el-option label="近12个月" :value="12" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="fetchAllData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 价格趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>价格趋势分析</span>
          <el-text type="info" size="small">展示近期房价变化趋势</el-text>
        </div>
      </template>
      <div v-loading="loading.priceTrend">
        <v-chart :option="priceTrendOption" style="height: 400px" autoresize />
      </div>
    </el-card>

    <!-- 区域对比 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>区域对比分析</span>
          <el-text type="info" size="small">对比各区域平均房价</el-text>
        </div>
      </template>
      <div v-loading="loading.districtComparison">
        <v-chart :option="districtComparisonOption" style="height: 400px" autoresize />
      </div>
    </el-card>

    <!-- 区域热度图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>🔥 区域热度分布图</span>
          <el-text type="info" size="small">基于房源数量、成交活跃度和价格综合评估</el-text>
        </div>
      </template>
      <div v-loading="loading.heatMap">
        <v-chart :option="districtHeatOption" style="height: 400px" autoresize />
      </div>
      <el-alert
        title="热度指数说明"
        type="info"
        :closable="false"
        style="margin-top: 15px"
      >
        <template #default>
          <p style="font-size: 12px; margin: 0;">
            热度指数综合考虑：在售房源数量（30%）+ 近30天成交数（50%权重）+ 平均价格（20%）
          </p>
        </template>
      </el-alert>
    </el-card>

    <!-- 房源分布可视化 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>📍 房源分布可视化</span>
          <el-text type="info" size="small">各区域房源数量与价格分布</el-text>
        </div>
      </template>
      <div v-loading="loading.houseMap">
        <v-chart :option="houseDistributionOption" style="height: 450px" autoresize />
      </div>
      <el-alert
        title="图表说明"
        type="info"
        :closable="false"
        style="margin-top: 15px"
      >
        <template #default>
          <p style="font-size: 12px; margin: 0;">
            气泡大小代表房源数量，颜色深浅代表平均价格（红色为高价区域，蓝色为低价区域）
          </p>
        </template>
      </el-alert>
    </el-card>

    <el-row :gutter="20">
      <!-- 户型分布 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>🏠 户型占比分布</span>
              <el-text type="info" size="small">各户型市场占比统计</el-text>
            </div>
          </template>
          <div v-loading="loading.houseTypeDistribution">
            <v-chart :option="houseTypeOption" style="height: 350px" autoresize />
          </div>
        </el-card>
      </el-col>

      <!-- 价格区间分布 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>💰 价格区间分布</span>
              <el-text type="info" size="small">不同价格区间房源数量</el-text>
            </div>
          </template>
          <div v-loading="loading.priceRangeDistribution">
            <v-chart :option="priceRangeOption" style="height: 350px" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 房价预测 -->
    <el-card class="predict-card">
      <template #header>
        <div class="card-header">
          <span>房价预测</span>
          <el-text type="info" size="small">基于历史数据预测房价</el-text>
        </div>
      </template>

      <el-form :inline="true" :model="predictForm" label-width="100px">
        <el-form-item label="区域">
          <el-select
            v-model="predictForm.district"
            placeholder="选择区域"
            style="width: 150px"
          >
            <el-option
              v-for="district in districts"
              :key="district.id"
              :label="district.name"
              :value="district.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="户型">
          <el-select
            v-model="predictForm.house_type"
            placeholder="选择户型"
            style="width: 120px"
          >
            <el-option label="1室" value="1室" />
            <el-option label="2室" value="2室" />
            <el-option label="3室" value="3室" />
            <el-option label="4室" value="4室" />
            <el-option label="5室及以上" value="5室及以上" />
          </el-select>
        </el-form-item>

        <el-form-item label="面积(㎡)">
          <el-input-number
            v-model="predictForm.area"
            :min="0"
            :step="10"
            style="width: 150px"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading.predict"
            @click="handlePredict"
          >
            预测价格
          </el-button>
        </el-form-item>
      </el-form>

      <el-alert
        v-if="predictResult"
        :title="`预测总价: ${formatPrice(predictResult.predicted_price)} 万元`"
        type="success"
        :closable="false"
        style="margin-top: 20px"
      >
        <template #default>
          <p>预测单价: {{ formatPrice(predictResult.predicted_unit_price) }} 元/㎡</p>
          <p>参考面积: {{ predictResult.area }} ㎡</p>
          <p>基于近6个月同区域、同户型的成交数据</p>
        </template>
      </el-alert>
    </el-card>

    <!-- 房源对比与分析报告 -->
    <el-card class="comparison-card">
      <template #header>
        <div class="card-header">
          <span>🔍 房源对比与分析报告</span>
          <el-text type="info" size="small">选择最多4个房源进行对比分析</el-text>
        </div>
      </template>

      <!-- 房源选择 -->
      <div class="house-selector">
        <el-form :inline="true">
          <el-form-item label="选择房源">
            <el-input
              v-model="comparisonForm.houseIds"
              placeholder="输入房源ID，用逗号分隔（如: 1,2,3,4）"
              style="width: 400px"
              clearable
            >
              <template #prepend>
                <el-icon><House /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              :loading="loading.comparison"
              @click="handleCompareHouses"
              :disabled="!comparisonForm.houseIds"
            >
              <el-icon><TrendCharts /></el-icon>
              开始对比
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-alert
          title="提示：您可以在房源列表页查看房源ID，或直接从详情页URL获取"
          type="info"
          :closable="false"
        />
      </div>

      <!-- 对比结果 -->
      <div v-if="comparisonResult && comparisonResult.houses.length > 0" class="comparison-result">
        <el-divider>
          <el-tag type="success" size="large">
            对比结果 ({{ comparisonResult.houses.length }}套房源)
          </el-tag>
        </el-divider>

        <!-- 对比表格 -->
        <el-table 
          :data="comparisonResult.houses" 
          border 
          stripe
          style="margin-bottom: 20px"
        >
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column label="价格" width="120">
            <template #default="{ row }">
              <span style="color: #f56c6c; font-weight: bold;">
                {{ formatPrice(row.price) }}万
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价(元/㎡)" width="130" />
          <el-table-column prop="house_type" label="户型" width="100" />
          <el-table-column prop="area" label="面积(㎡)" width="100" />
          <el-table-column prop="district_name" label="区域" width="120" />
          <el-table-column label="综合评分" width="120">
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.score)">
                {{ row.score }}分
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <!-- 对比雷达图 -->
        <div class="comparison-charts">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>综合对比雷达图</template>
                <v-chart :option="comparisonRadarOption" style="height: 350px" autoresize />
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>价格对比柱状图</template>
                <v-chart :option="comparisonBarOption" style="height: 350px" autoresize />
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 分析报告 -->
        <el-card shadow="hover" class="report-card" style="margin-top: 20px">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📊 智能分析报告</span>
              <el-button 
                type="success" 
                size="small"
                @click="downloadReport"
              >
                <el-icon><Download /></el-icon>
                下载报告
              </el-button>
            </div>
          </template>

          <div class="report-content" id="reportContent">
            <!-- 报告标题 -->
            <div class="report-header">
              <h2>房源对比分析报告</h2>
              <p class="report-date">生成时间: {{ new Date().toLocaleString('zh-CN') }}</p>
            </div>

            <!-- 概况 -->
            <div class="report-section">
              <h3>📌 对比概况</h3>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="对比房源数">
                  {{ comparisonResult.houses.length }} 套
                </el-descriptions-item>
                <el-descriptions-item label="价格区间">
                  {{ formatPrice(comparisonResult.summary.min_price) }}万 - 
                  {{ formatPrice(comparisonResult.summary.max_price) }}万
                </el-descriptions-item>
                <el-descriptions-item label="平均总价">
                  {{ formatPrice(comparisonResult.summary.avg_price) }} 万
                </el-descriptions-item>
                <el-descriptions-item label="平均单价">
                  {{ formatPrice(comparisonResult.summary.avg_unit_price) }} 元/㎡
                </el-descriptions-item>
                <el-descriptions-item label="最优性价比">
                  ID: {{ comparisonResult.recommendation.best_value.id }} - 
                  {{ comparisonResult.recommendation.best_value.title }}
                </el-descriptions-item>
                <el-descriptions-item label="最低单价">
                  ID: {{ comparisonResult.recommendation.lowest_unit_price.id }} - 
                  {{ formatPrice(comparisonResult.recommendation.lowest_unit_price.unit_price) }} 元/㎡
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 推荐结果 -->
            <div class="report-section">
              <h3>⭐ 推荐结果</h3>
              <el-alert 
                :title="`最具性价比: ${comparisonResult.recommendation.best_value.title}`"
                type="success"
                :closable="false"
                style="margin-bottom: 10px"
              >
                <template #default>
                  <p>价格: {{ formatPrice(comparisonResult.recommendation.best_value.price) }}万</p>
                  <p>单价: {{ formatPrice(comparisonResult.recommendation.best_value.unit_price) }} 元/㎡</p>
                  <p>综合评分: {{ comparisonResult.recommendation.best_value.score }}分</p>
                </template>
              </el-alert>

              <el-alert 
                :title="`最低单价: ${comparisonResult.recommendation.lowest_unit_price.title}`"
                type="info"
                :closable="false"
              >
                <template #default>
                  <p>单价: {{ formatPrice(comparisonResult.recommendation.lowest_unit_price.unit_price) }} 元/㎡</p>
                  <p>总价: {{ formatPrice(comparisonResult.recommendation.lowest_unit_price.price) }}万</p>
                </template>
              </el-alert>
            </div>

            <!-- 详细对比 -->
            <div class="report-section">
              <h3>📋 详细对比</h3>
              <div v-for="house in comparisonResult.houses" :key="house.id" class="house-detail-item">
                <h4>{{ house.title }} (ID: {{ house.id }})</h4>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <p><strong>总价:</strong> {{ formatPrice(house.price) }}万</p>
                    <p><strong>单价:</strong> {{ formatPrice(house.unit_price) }} 元/㎡</p>
                    <p><strong>户型:</strong> {{ house.house_type }}</p>
                    <p><strong>面积:</strong> {{ house.area }} ㎡</p>
                  </el-col>
                  <el-col :span="12">
                    <p><strong>区域:</strong> {{ house.district_name }}</p>
                    <p><strong>地址:</strong> {{ house.address }}</p>
                    <p><strong>楼层:</strong> {{ house.floor }}/{{ house.total_floors }}层</p>
                    <p><strong>综合评分:</strong> {{ house.score }}分</p>
                  </el-col>
                </el-row>
                <el-divider />
              </div>
            </div>

            <!-- 分析建议 -->
            <div class="report-section">
              <h3>💡 购房建议</h3>
              <el-timeline>
                <el-timeline-item 
                  v-for="(suggestion, index) in comparisonResult.suggestions" 
                  :key="index"
                  :icon="index === 0 ? 'StarFilled' : 'More'"
                  :type="index === 0 ? 'success' : 'primary'"
                >
                  {{ suggestion }}
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 空状态 -->
      <el-empty v-else-if="!loading.comparison" description="请输入房源ID开始对比" />
    </el-card>

    <!-- 经纪人专属功能 -->
    <div v-if="isAgent" class="agent-section">
      <el-divider content-position="left">
        <el-tag type="warning" size="large">
          <el-icon><Star /></el-icon>
          经纪人专属分析工具
        </el-tag>
      </el-divider>

      <el-row :gutter="20">
        <!-- 投资回报分析 -->
        <el-col :span="12">
          <el-card class="agent-card">
            <template #header>
              <div class="card-header">
                <span>💰 投资回报率分析</span>
                <el-text type="info" size="small">评估房产投资价值</el-text>
              </div>
            </template>

            <el-form :model="roiForm" label-width="110px">
              <el-form-item label="房源ID" tooltip="可选，用于价格合理性对比">
                <el-input-number
                  v-model="roiForm.house_id"
                  :min="0"
                  :controls="false"
                  placeholder="选填"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="购入价格" required>
                <el-input-number
                  v-model="roiForm.purchase_price"
                  :min="0"
                  :step="10"
                  style="width: 100%"
                >
                  <template #append>万元</template>
                </el-input-number>
              </el-form-item>

              <el-form-item label="预期月租金" required>
                <el-input-number
                  v-model="roiForm.monthly_rent"
                  :min="0"
                  :step="100"
                  style="width: 100%"
                >
                  <template #append>元</template>
                </el-input-number>
              </el-form-item>

              <el-form-item label="月物业费">
                <el-input-number
                  v-model="roiForm.property_fee"
                  :min="0"
                  :step="10"
                  style="width: 100%"
                >
                  <template #append>元</template>
                </el-input-number>
              </el-form-item>

              <el-form-item label="其他月成本">
                <el-input-number
                  v-model="roiForm.other_costs"
                  :min="0"
                  :step="10"
                  style="width: 100%"
                >
                  <template #append>元</template>
                </el-input-number>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  :loading="loading.roi"
                  @click="handleRoiAnalysis"
                  style="width: 100%"
                >
                  <el-icon><TrendCharts /></el-icon>
                  开始分析
                </el-button>
              </el-form-item>
            </el-form>

            <!-- ROI分析结果 -->
            <div v-if="roiResult" class="roi-result">
              <el-divider>分析结果</el-divider>
              
              <el-descriptions :column="2" border>
                <el-descriptions-item label="毛回报率">
                  <el-tag :type="roiResult.gross_roi > 4 ? 'success' : 'warning'" size="large">
                    {{ roiResult.gross_roi }}%
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="净回报率">
                  <el-tag :type="getRoiLevelType(roiResult.reasonability_level)" size="large">
                    {{ roiResult.net_roi }}%
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="年租金收入">
                  {{ formatPrice(roiResult.annual_income) }} 元
                </el-descriptions-item>
                <el-descriptions-item label="年成本">
                  {{ formatPrice(roiResult.annual_cost) }} 元
                </el-descriptions-item>
                <el-descriptions-item label="净年收入">
                  {{ formatPrice(roiResult.net_annual_income) }} 元
                </el-descriptions-item>
                <el-descriptions-item label="回本周期">
                  <span v-if="roiResult.payback_period">
                    {{ roiResult.payback_period }} 年
                  </span>
                  <el-tag v-else type="danger">无法回本</el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <el-alert
                :title="roiResult.price_reasonability"
                :type="getRoiLevelType(roiResult.reasonability_level)"
                :closable="false"
                style="margin-top: 15px"
              >
                <template #default v-if="roiResult.district_name">
                  <p>区域: {{ roiResult.district_name }}</p>
                  <p>区域均价: {{ formatPrice(roiResult.district_avg_price) }} 万元</p>
                  <p>价格差异: 
                    <span :class="roiResult.price_diff_percent > 0 ? 'text-danger' : 'text-success'">
                      {{ roiResult.price_diff_percent > 0 ? '+' : '' }}{{ roiResult.price_diff_percent }}%
                    </span>
                  </p>
                </template>
              </el-alert>
            </div>
          </el-card>
        </el-col>

        <!-- 市场趋势预测 -->
        <el-col :span="12">
          <el-card class="agent-card">
            <template #header>
              <div class="card-header">
                <span>📈 市场趋势预测分析</span>
                <el-text type="info" size="small">实时市场动态监测</el-text>
              </div>
            </template>

            <div v-loading="loading.marketTrend">
              <!-- 市场热度仪表盘 -->
              <div class="market-heat-gauge">
                <v-chart :option="marketHeatOption" style="height: 280px" autoresize />
              </div>

              <!-- 市场数据 -->
              <div v-if="marketTrendData" class="market-data">
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="供需比">
                    {{ marketTrendData.supply_demand_ratio }}
                    <el-tooltip content="在售房源数 / 近30天成交量">
                      <el-icon><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </el-descriptions-item>
                  <el-descriptions-item label="成交活跃度">
                    <el-tag :type="getActivityType(marketTrendData.activity_level)">
                      {{ marketTrendData.transaction_activity }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="在售房源">
                    {{ marketTrendData.supply_count }} 套
                  </el-descriptions-item>
                  <el-descriptions-item label="近30天成交">
                    {{ marketTrendData.demand_count }} 套
                  </el-descriptions-item>
                  <el-descriptions-item label="价格趋势">
                    <el-tag :type="getTrendType(marketTrendData.trend_direction)" size="large">
                      {{ marketTrendData.price_trend }}
                      <span v-if="marketTrendData.price_change_percent !== 0">
                        ({{ marketTrendData.price_change_percent > 0 ? '+' : '' }}{{ marketTrendData.price_change_percent }}%)
                      </span>
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="当前均价">
                    {{ formatPrice(marketTrendData.current_avg_price) }} 万元
                  </el-descriptions-item>
                </el-descriptions>

                <!-- 价格预测 -->
                <el-card shadow="never" style="margin-top: 15px; background: #f5f7fa">
                  <template #header>
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <el-icon color="#409eff"><TrendCharts /></el-icon>
                      <span style="font-weight: bold;">下月价格预测</span>
                    </div>
                  </template>
                  <div class="forecast-box">
                    <div class="forecast-price">
                      {{ formatPrice(marketTrendData.forecast_next_month) }} 万元
                    </div>
                    <div class="forecast-change">
                      预计变化: 
                      <span :class="marketTrendData.forecast_change_percent > 0 ? 'text-danger' : 'text-success'">
                        {{ marketTrendData.forecast_change_percent > 0 ? '↑' : '↓' }}
                        {{ Math.abs(marketTrendData.forecast_change_percent) }}%
                      </span>
                    </div>
                  </div>
                </el-card>

                <!-- 市场建议 -->
                <el-alert
                  :title="marketTrendData.market_suggestion"
                  type="info"
                  :closable="false"
                  style="margin-top: 15px"
                  show-icon
                >
                  <template #default>
                    <p style="font-size: 12px; color: #909399; margin: 0;">
                      分析日期: {{ marketTrendData.analysis_date }}
                    </p>
                  </template>
                </el-alert>
              </div>

              <el-empty v-else description="暂无数据" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart, GaugeChart, RadarChart, ScatterChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  getPriceTrend,
  getDistrictComparison,
  getHouseTypeDistribution,
  getPriceRangeDistribution,
  predictPrice,
  roiAnalysis,
  marketTrendForecast,
  getDistrictHeatMap
} from '@/api/analysis'
import { getMapData, getHouseDetail } from '@/api/house'
import { getDistrictList } from '@/api/house'
import { formatPrice } from '@/utils'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  GaugeChart,
  RadarChart,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent
])

const userStore = useUserStore()

// 判断是否为经纪人
const isAgent = computed(() => {
  return userStore.userInfo?.role === 'agent' || userStore.userInfo?.role === 'admin'
})

const districts = ref([])
const filterForm = reactive({
  district: '',
  months: 6
})

const predictForm = reactive({
  district: '',
  house_type: '',
  area: 100
})

const predictResult = ref(null)

// 经纪人专属：投资回报分析表单
const roiForm = reactive({
  house_id: '',
  purchase_price: 300,
  monthly_rent: 5000,
  property_fee: 300,
  other_costs: 200
})

const roiResult = ref(null)

// 经纪人专属：市场趋势分析
const marketTrendData = ref(null)

// 区域热度图数据
const heatMapData = ref([])

// 房源地图分布数据
const houseMapData = ref(null)

// 房源对比表单
const comparisonForm = reactive({
  houseIds: ''
})

// 对比结果
const comparisonResult = ref(null)

const loading = reactive({
  priceTrend: false,
  districtComparison: false,
  houseTypeDistribution: false,
  priceRangeDistribution: false,
  predict: false,
  roi: false,
  marketTrend: false,
  heatMap: false,
  houseMap: false,
  comparison: false
})

// 价格趋势图配置
const priceTrendOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['平均总价', '平均单价']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: []
  },
  yAxis: [
    {
      type: 'value',
      name: '总价(万元)',
      position: 'left'
    },
    {
      type: 'value',
      name: '单价(元/㎡)',
      position: 'right'
    }
  ],
  series: [
    {
      name: '平均总价',
      type: 'line',
      data: [],
      smooth: true,
      yAxisIndex: 0
    },
    {
      name: '平均单价',
      type: 'line',
      data: [],
      smooth: true,
      yAxisIndex: 1
    }
  ]
})

// 区域对比图配置
const districtComparisonOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['平均总价', '平均单价']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: []
  },
  yAxis: [
    {
      type: 'value',
      name: '总价(万元)'
    },
    {
      type: 'value',
      name: '单价(元/㎡)'
    }
  ],
  series: [
    {
      name: '平均总价',
      type: 'bar',
      data: [],
      yAxisIndex: 0
    },
    {
      name: '平均单价',
      type: 'bar',
      data: [],
      yAxisIndex: 1
    }
  ]
})

// 户型分布图配置
const houseTypeOption = ref({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '户型分布',
      type: 'pie',
      radius: '50%',
      data: [],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
})

// 价格区间分布图配置
const priceRangeOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: []
  },
  yAxis: {
    type: 'value',
    name: '房源数量'
  },
  series: [
    {
      name: '房源数量',
      type: 'bar',
      data: [],
      itemStyle: {
        color: '#409eff'
      }
    }
  ]
})

// 区域热度图配置
const districtHeatOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: function(params) {
      const data = params[0]
      const dataIndex = data.dataIndex
      const heatData = heatMapData.value[dataIndex]
      if (!heatData) return data.name
      
      return `
        <strong>${data.name}</strong><br/>
        热度指数: ${data.value}<br/>
        在售房源: ${heatData.available_count} 套<br/>
        近30天成交: ${heatData.transaction_count} 套<br/>
        平均价格: ${heatData.avg_price} 万元
      `
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: [],
    axisLabel: {
      interval: 0,
      rotate: 45
    }
  },
  yAxis: {
    type: 'value',
    name: '热度指数'
  },
  visualMap: {
    min: 0,
    max: 100,
    text: ['高', '低'],
    realtime: false,
    calculable: true,
    inRange: {
      color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
    }
  },
  series: [
    {
      name: '热度指数',
      type: 'bar',
      data: [],
      itemStyle: {
        borderRadius: [5, 5, 0, 0]
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}'
      }
    }
  ]
})

// 房源分布散点图配置
const houseDistributionOption = ref({
  tooltip: {
    trigger: 'item',
    formatter: function(params) {
      return `
        <strong>${params.data.district_name}</strong><br/>
        房源数量: ${params.data.value[2]} 套<br/>
        平均价格: ${params.data.avg_price} 万元
      `
    }
  },
  grid: {
    left: '10%',
    right: '10%',
    bottom: '10%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    name: '区域编号',
    axisLabel: {
      formatter: '{value}'
    }
  },
  yAxis: {
    type: 'value',
    name: '房源数量',
    axisLabel: {
      formatter: '{value} 套'
    }
  },
  visualMap: {
    min: 0,
    max: 500,
    dimension: 3,
    orient: 'vertical',
    right: 10,
    top: 'center',
    text: ['高价', '低价'],
    calculable: true,
    inRange: {
      color: ['#50a3ba', '#eac736', '#d94e5d']
    }
  },
  series: [
    {
      name: '房源分布',
      type: 'scatter',
      symbolSize: function(data) {
        return Math.sqrt(data[2]) * 3
      },
      data: [],
      animationDelay: function(idx) {
        return idx * 5
      }
    }
  ]
})

// 房源对比雷达图配置
const comparisonRadarOption = ref({
  tooltip: {},
  legend: {
    data: []
  },
  radar: {
    indicator: [
      { name: '价格优势', max: 100 },
      { name: '面积', max: 100 },
      { name: '楼层', max: 100 },
      { name: '区域热度', max: 100 },
      { name: '性价比', max: 100 }
    ]
  },
  series: [
    {
      name: '房源对比',
      type: 'radar',
      data: []
    }
  ]
})

// 房源对比柱状图配置
const comparisonBarOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['总价', '单价']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: []
  },
  yAxis: [
    {
      type: 'value',
      name: '总价(万元)'
    },
    {
      type: 'value',
      name: '单价(元/㎡)'
    }
  ],
  series: [
    {
      name: '总价',
      type: 'bar',
      data: [],
      yAxisIndex: 0
    },
    {
      name: '单价',
      type: 'bar',
      data: [],
      yAxisIndex: 1
    }
  ]
})

// 市场热度仪表盘配置
const marketHeatOption = ref({
  series: [
    {
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      center: ['50%', '75%'],
      radius: '90%',
      axisLine: {
        lineStyle: {
          width: 30,
          color: [
            [0.3, '#fd666d'],
            [0.7, '#67e0e3'],
            [1, '#37a2da']
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '12%',
        width: 20,
        offsetCenter: [0, '-60%'],
        itemStyle: {
          color: 'auto'
        }
      },
      axisTick: {
        length: 12,
        lineStyle: {
          color: 'auto',
          width: 2
        }
      },
      splitLine: {
        length: 20,
        lineStyle: {
          color: 'auto',
          width: 5
        }
      },
      axisLabel: {
        color: '#464646',
        fontSize: 14,
        distance: -60,
        rotate: 'tangential',
        formatter: function (value) {
          if (value === 0) return '冷'
          if (value === 50) return '温'
          if (value === 100) return '热'
          return ''
        }
      },
      title: {
        offsetCenter: [0, '-10%'],
        fontSize: 20
      },
      detail: {
        fontSize: 30,
        offsetCenter: [0, '-35%'],
        valueAnimation: true,
        formatter: '{value}',
        color: 'auto'
      },
      data: [
        {
          value: 0,
          name: '市场热度'
        }
      ]
    }
  ]
})

async function fetchDistricts() {
  try {
    const res = await getDistrictList()
    if (res.code === 200) {
      // 处理多种可能的响应格式
      if (Array.isArray(res.data)) {
        districts.value = res.data
      } else if (res.data.results) {
        districts.value = res.data.results
      } else {
        districts.value = []
      }
      console.log('区域列表:', districts.value)
    }
  } catch (error) {
    console.error('获取区域列表失败:', error)
  }
}

async function fetchPriceTrend() {
  loading.priceTrend = true
  try {
    const params = {
      days: filterForm.months * 30  // 后端期望days参数
    }
    if (filterForm.district) {
      params.district_id = filterForm.district  // 后端期望district_id参数
    }

    console.log('价格趋势请求参数:', params)
    const res = await getPriceTrend(params)
    console.log('价格趋势响应:', res)
    
    if (res.code === 200) {
      const data = res.data
      const trend = data.trend || []
      
      // 提取月份和价格数据
      const months = trend.map(item => item.month)
      const avgPrices = trend.map(item => item.avg_price)
      const avgUnitPrices = trend.map(item => item.avg_unit_price)
      
      console.log('价格趋势数据:', { months, avgPrices, avgUnitPrices })
      
      priceTrendOption.value.xAxis.data = months
      priceTrendOption.value.series[0].data = avgPrices
      priceTrendOption.value.series[1].data = avgUnitPrices
    }
  } catch (error) {
    console.error('获取价格趋势失败:', error)
    ElMessage.error('获取价格趋势失败')
  } finally {
    loading.priceTrend = false
  }
}

async function fetchDistrictComparison() {
  loading.districtComparison = true
  try {
    console.log('获取区域对比数据...')
    const res = await getDistrictComparison()
    console.log('区域对比响应:', res)
    
    if (res.code === 200) {
      const data = Array.isArray(res.data) ? res.data : []
      
      // 提取区域名称和价格数据
      const districts = data.map(item => item.district_name)
      const avgPrices = data.map(item => item.avg_price)
      const avgUnitPrices = data.map(item => item.avg_unit_price)
      
      console.log('区域对比数据:', { districts, avgPrices, avgUnitPrices })
      
      districtComparisonOption.value.xAxis.data = districts
      districtComparisonOption.value.series[0].data = avgPrices
      districtComparisonOption.value.series[1].data = avgUnitPrices
    }
  } catch (error) {
    console.error('获取区域对比失败:', error)
    ElMessage.error('获取区域对比失败')
  } finally {
    loading.districtComparison = false
  }
}

async function fetchHouseTypeDistribution() {
  loading.houseTypeDistribution = true
  try {
    const params = {}
    if (filterForm.district) {
      params.district_id = filterForm.district  // 后端期望district_id参数
    }

    console.log('户型分布请求参数:', params)
    const res = await getHouseTypeDistribution(params)
    console.log('户型分布响应:', res)
    
    if (res.code === 200) {
      const data = res.data
      const distribution = data.distribution || []
      
      // 转换为ECharts需要的格式
      const chartData = distribution.map(item => ({
        name: item.house_type,
        value: item.count
      }))
      
      console.log('户型分布数据:', chartData)
      houseTypeOption.value.series[0].data = chartData
    }
  } catch (error) {
    console.error('获取户型分布失败:', error)
    ElMessage.error('获取户型分布失败')
  } finally {
    loading.houseTypeDistribution = false
  }
}

async function fetchPriceRangeDistribution() {
  loading.priceRangeDistribution = true
  try {
    const params = {}
    if (filterForm.district) {
      params.district_id = filterForm.district  // 后端期望district_id参数
    }

    console.log('价格区间分布请求参数:', params)
    const res = await getPriceRangeDistribution(params)
    console.log('价格区间分布响应:', res)
    
    if (res.code === 200) {
      const data = res.data
      const distribution = data.distribution || []
      
      // 提取区间和数量数据
      const ranges = distribution.map(item => item.range)
      const counts = distribution.map(item => item.count)
      
      console.log('价格区间分布数据:', { ranges, counts })
      
      priceRangeOption.value.xAxis.data = ranges
      priceRangeOption.value.series[0].data = counts
    }
  } catch (error) {
    console.error('获取价格区间分布失败:', error)
    ElMessage.error('获取价格区间分布失败')
  } finally {
    loading.priceRangeDistribution = false
  }
}

async function handlePredict() {
  if (!predictForm.district || !predictForm.house_type || !predictForm.area) {
    ElMessage.warning('请填写完整的预测信息')
    return
  }

  loading.predict = true
  try {
    const data = {
      district_id: predictForm.district,  // 后端期望district_id参数
      house_type: predictForm.house_type,
      area: predictForm.area
    }
    
    console.log('房价预测请求参数:', data)
    const res = await predictPrice(data)
    console.log('房价预测响应:', res)
    
    if (res.code === 200) {
      predictResult.value = {
        ...res.data,
        predicted_unit_price: res.data.median_unit_price  // 使用median_unit_price作为单价
      }
      console.log('预测结果:', predictResult.value)
      ElMessage.success('预测成功')
    }
  } catch (error) {
    console.error('预测失败:', error)
    let errorMsg = '预测失败'
    if (error.response && error.response.data) {
      errorMsg = error.response.data.msg || errorMsg
    }
    ElMessage.error(errorMsg)
  } finally {
    loading.predict = false
  }
}

// 投资回报分析
async function handleRoiAnalysis() {
  if (!roiForm.purchase_price || !roiForm.monthly_rent) {
    ElMessage.warning('请填写购入价格和月租金')
    return
  }

  loading.roi = true
  try {
    const data = {
      purchase_price: roiForm.purchase_price,
      monthly_rent: roiForm.monthly_rent,
      property_fee: roiForm.property_fee,
      other_costs: roiForm.other_costs
    }
    
    if (roiForm.house_id) {
      data.house_id = roiForm.house_id
    }
    
    const res = await roiAnalysis(data)
    if (res.code === 200) {
      roiResult.value = res.data
      ElMessage.success('分析完成')
    }
  } catch (error) {
    console.error('ROI分析失败:', error)
    let errorMsg = '分析失败'
    if (error.response && error.response.data) {
      errorMsg = error.response.data.msg || errorMsg
    }
    ElMessage.error(errorMsg)
  } finally {
    loading.roi = false
  }
}

// 市场趋势预测
async function fetchMarketTrend() {
  loading.marketTrend = true
  try {
    const params = {}
    if (filterForm.district) {
      params.district_id = filterForm.district
    }
    
    const res = await marketTrendForecast(params)
    if (res.code === 200) {
      marketTrendData.value = res.data
      
      // 更新市场热度仪表盘
      marketHeatOption.value.series[0].data[0].value = res.data.market_heat
      
      ElMessage.success('市场趋势分析完成')
    }
  } catch (error) {
    console.error('市场趋势分析失败:', error)
    let errorMsg = '分析失败'
    if (error.response && error.response.data) {
      errorMsg = error.response.data.msg || errorMsg
    }
    ElMessage.error(errorMsg)
  } finally {
    loading.marketTrend = false
  }
}

// 获取ROI等级的标签类型
function getRoiLevelType(level) {
  const typeMap = {
    'excellent': 'success',
    'good': 'success',
    'fair': 'warning',
    'poor': 'danger',
    'unknown': 'info'
  }
  return typeMap[level] || 'info'
}

// 获取价格趋势的标签类型
function getTrendType(direction) {
  const typeMap = {
    'up': 'danger',
    'stable': 'success',
    'down': 'primary',
    'unknown': 'info'
  }
  return typeMap[direction] || 'info'
}

// 获取活跃度标签类型
function getActivityType(level) {
  const typeMap = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return typeMap[level] || 'info'
}

// 获取区域热度图数据
async function fetchDistrictHeatMap() {
  loading.heatMap = true
  try {
    const res = await getDistrictHeatMap()
    if (res.code === 200) {
      heatMapData.value = res.data
      
      // 更新图表数据
      const districts = res.data.map(item => item.district_name)
      const heatValues = res.data.map(item => item.heat_percentage)
      
      districtHeatOption.value.xAxis.data = districts
      districtHeatOption.value.series[0].data = heatValues
    }
  } catch (error) {
    console.error('获取区域热度图失败:', error)
    ElMessage.error('获取区域热度图失败')
  } finally {
    loading.heatMap = false
  }
}

// 获取房源分布数据
async function fetchHouseDistribution() {
  loading.houseMap = true
  try {
    const res = await getMapData({})
    if (res.code === 200) {
      houseMapData.value = res.data
      
      // 统计各区域房源数量
      const districtStats = {}
      const features = res.data.features || []
      
      features.forEach(feature => {
        const props = feature.properties
        // 确保有区域名称
        const districtName = props.district_name && props.district_name !== '未知区域' 
          ? props.district_name 
          : `区域${props.district || '未知'}`
        
        if (!districtStats[districtName]) {
          districtStats[districtName] = {
            count: 0,
            totalPrice: 0,
            district_id: props.district
          }
        }
        
        districtStats[districtName].count++
        districtStats[districtName].totalPrice += parseFloat(props.price || 0)
      })
      
      // 转换为散点图数据
      const scatterData = []
      let maxPrice = 0
      
      Object.keys(districtStats).forEach((districtName, index) => {
        const stats = districtStats[districtName]
        const avgPrice = stats.count > 0 ? stats.totalPrice / stats.count : 0
        
        if (avgPrice > maxPrice) {
          maxPrice = avgPrice
        }
        
        scatterData.push({
          value: [
            index + 1,  // x: 区域编号
            stats.count,  // y: 房源数量
            stats.count,  // size: 气泡大小
            avgPrice  // color: 价格映射颜色
          ],
          district_name: districtName,
          avg_price: avgPrice.toFixed(2),
          count: stats.count
        })
      })
      
      // 更新visualMap的最大值
      houseDistributionOption.value.visualMap.max = maxPrice
      houseDistributionOption.value.series[0].data = scatterData
    }
  } catch (error) {
    console.error('获取房源分布失败:', error)
    ElMessage.error('获取房源分布失败')
  } finally {
    loading.houseMap = false
  }
}

// 房源对比
async function handleCompareHouses() {
  if (!comparisonForm.houseIds) {
    ElMessage.warning('请输入房源ID')
    return
  }

  // 解析房源ID
  const ids = comparisonForm.houseIds.split(',').map(id => id.trim()).filter(id => id)
  
  if (ids.length < 2) {
    ElMessage.warning('请至少选择2个房源进行对比')
    return
  }

  if (ids.length > 4) {
    ElMessage.warning('最多只能对比4个房源')
    return
  }

  loading.comparison = true
  try {
    // 获取所有房源详情
    const housePromises = ids.map(id => getHouseDetail(id))
    const responses = await Promise.all(housePromises)
    
    const houses = responses
      .filter(res => res.code === 200)
      .map(res => res.data)

    if (houses.length === 0) {
      ElMessage.error('未找到有效的房源')
      return
    }

    // 计算统计数据
    const prices = houses.map(h => h.price)
    const unitPrices = houses.map(h => h.unit_price)
    const areas = houses.map(h => h.area)
    
    const summary = {
      min_price: Math.min(...prices),
      max_price: Math.max(...prices),
      avg_price: (prices.reduce((a, b) => a + b, 0) / prices.length).toFixed(2),
      avg_unit_price: (unitPrices.reduce((a, b) => a + b, 0) / unitPrices.length).toFixed(2)
    }

    // 计算每个房源的综合评分
    const housesWithScore = houses.map(house => {
      // 价格分数（价格越低分数越高）
      const priceScore = ((summary.max_price - house.price) / (summary.max_price - summary.min_price || 1)) * 100
      
      // 单价分数
      const maxUnitPrice = Math.max(...unitPrices)
      const minUnitPrice = Math.min(...unitPrices)
      const unitPriceScore = ((maxUnitPrice - house.unit_price) / (maxUnitPrice - minUnitPrice || 1)) * 100
      
      // 面积分数
      const maxArea = Math.max(...areas)
      const areaScore = (house.area / maxArea) * 100
      
      // 楼层分数（中间楼层较好）
      const floorRatio = house.floor / house.total_floors
      const floorScore = (1 - Math.abs(floorRatio - 0.5) * 2) * 100
      
      // 区域热度分数（简单模拟）
      const districtScore = 70 + Math.random() * 30
      
      // 综合评分
      const score = (
        priceScore * 0.3 +
        unitPriceScore * 0.3 +
        areaScore * 0.2 +
        floorScore * 0.1 +
        districtScore * 0.1
      ).toFixed(1)

      return {
        ...house,
        score: parseFloat(score),
        priceScore: priceScore.toFixed(1),
        unitPriceScore: unitPriceScore.toFixed(1),
        areaScore: areaScore.toFixed(1),
        floorScore: floorScore.toFixed(1),
        districtScore: districtScore.toFixed(1)
      }
    })

    // 排序找出推荐
    const sortedByScore = [...housesWithScore].sort((a, b) => b.score - a.score)
    const sortedByUnitPrice = [...housesWithScore].sort((a, b) => a.unit_price - b.unit_price)

    // 生成建议
    const suggestions = [
      `综合评分最高的是"${sortedByScore[0].title}"，建议优先考虑。`,
      `单价最低的是"${sortedByUnitPrice[0].title}"，性价比较高。`,
      `平均总价${summary.avg_price}万元，平均单价${summary.avg_unit_price}元/㎡。`,
      houses.length >= 3 ? `共对比${houses.length}套房源，价格区间${summary.min_price}-${summary.max_price}万元。` : ''
    ].filter(s => s)

    comparisonResult.value = {
      houses: housesWithScore,
      summary,
      recommendation: {
        best_value: sortedByScore[0],
        lowest_unit_price: sortedByUnitPrice[0]
      },
      suggestions
    }

    // 更新图表
    updateComparisonCharts(housesWithScore)
    
    ElMessage.success('对比完成')
  } catch (error) {
    console.error('对比失败:', error)
    ElMessage.error('对比失败，请检查房源ID是否正确')
  } finally {
    loading.comparison = false
  }
}

// 更新对比图表
function updateComparisonCharts(houses) {
  // 更新雷达图
  const radarData = houses.map(house => ({
    name: `ID ${house.id}`,
    value: [
      parseFloat(house.priceScore),
      parseFloat(house.areaScore),
      parseFloat(house.floorScore),
      parseFloat(house.districtScore),
      house.score
    ]
  }))

  comparisonRadarOption.value.legend.data = houses.map(h => `ID ${h.id}`)
  comparisonRadarOption.value.series[0].data = radarData

  // 更新柱状图
  comparisonBarOption.value.xAxis.data = houses.map(h => `ID ${h.id}`)
  comparisonBarOption.value.series[0].data = houses.map(h => h.price)
  comparisonBarOption.value.series[1].data = houses.map(h => h.unit_price)
}

// 下载报告
function downloadReport() {
  const reportContent = document.getElementById('reportContent')
  if (!reportContent) {
    ElMessage.error('报告内容不存在')
    return
  }

  // 简单的文本版报告
  let reportText = '房源对比分析报告\n'
  reportText += '='.repeat(50) + '\n\n'
  reportText += `生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`
  
  reportText += '对比概况\n'
  reportText += '-'.repeat(50) + '\n'
  reportText += `对比房源数: ${comparisonResult.value.houses.length}套\n`
  reportText += `价格区间: ${formatPrice(comparisonResult.value.summary.min_price)}万 - ${formatPrice(comparisonResult.value.summary.max_price)}万\n`
  reportText += `平均总价: ${formatPrice(comparisonResult.value.summary.avg_price)}万\n`
  reportText += `平均单价: ${formatPrice(comparisonResult.value.summary.avg_unit_price)}元/㎡\n\n`
  
  reportText += '推荐结果\n'
  reportText += '-'.repeat(50) + '\n'
  reportText += `最具性价比: ${comparisonResult.value.recommendation.best_value.title}\n`
  reportText += `  价格: ${formatPrice(comparisonResult.value.recommendation.best_value.price)}万\n`
  reportText += `  单价: ${formatPrice(comparisonResult.value.recommendation.best_value.unit_price)}元/㎡\n`
  reportText += `  评分: ${comparisonResult.value.recommendation.best_value.score}分\n\n`
  
  reportText += '详细对比\n'
  reportText += '-'.repeat(50) + '\n'
  comparisonResult.value.houses.forEach(house => {
    reportText += `\n${house.title} (ID: ${house.id})\n`
    reportText += `  总价: ${formatPrice(house.price)}万\n`
    reportText += `  单价: ${formatPrice(house.unit_price)}元/㎡\n`
    reportText += `  户型: ${house.house_type}\n`
    reportText += `  面积: ${house.area}㎡\n`
    reportText += `  区域: ${house.district_name}\n`
    reportText += `  地址: ${house.address}\n`
    reportText += `  综合评分: ${house.score}分\n`
  })
  
  reportText += '\n购房建议\n'
  reportText += '-'.repeat(50) + '\n'
  comparisonResult.value.suggestions.forEach((suggestion, index) => {
    reportText += `${index + 1}. ${suggestion}\n`
  })

  // 创建并下载文件
  const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `房源对比分析报告_${Date.now()}.txt`
  link.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('报告已下载')
}

// 获取评分类型
function getScoreType(score) {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

function fetchAllData() {
  fetchPriceTrend()
  fetchDistrictComparison()
  fetchHouseTypeDistribution()
  fetchPriceRangeDistribution()
  fetchDistrictHeatMap()
  fetchHouseDistribution()
  
  // 如果是经纪人，同时获取市场趋势
  if (isAgent.value) {
    fetchMarketTrend()
  }
}

onMounted(() => {
  fetchDistricts()
  fetchAllData()
})
</script>

<style lang="scss" scoped>
.analysis-page {
  .filter-card {
    margin-bottom: 20px;
  }

  .chart-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .predict-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  // 经纪人专属功能样式
  .agent-section {
    margin-top: 30px;

    .agent-card {
      height: 100%;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .roi-result {
        margin-top: 20px;

        .text-danger {
          color: #f56c6c;
          font-weight: bold;
        }

        .text-success {
          color: #67c23a;
          font-weight: bold;
        }
      }

      .market-heat-gauge {
        margin-bottom: 20px;
      }

      .market-data {
        .forecast-box {
          text-align: center;
          padding: 15px;

          .forecast-price {
            font-size: 28px;
            font-weight: bold;
            color: #409eff;
            margin-bottom: 10px;
          }

          .forecast-change {
            font-size: 14px;
            color: #606266;

            .text-danger {
              color: #f56c6c;
              font-weight: bold;
            }

            .text-success {
              color: #67c23a;
              font-weight: bold;
            }
          }
        }
      }
    }
  }

  // 通用文本颜色类
  .text-danger {
    color: #f56c6c;
  }

  .text-success {
    color: #67c23a;
  }

  // 房源对比样式
  .comparison-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .house-selector {
      margin-bottom: 20px;
    }

    .comparison-result {
      .comparison-charts {
        margin: 20px 0;
      }

      .report-card {
        .report-content {
          .report-header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e4e7ed;

            h2 {
              font-size: 28px;
              color: #303133;
              margin-bottom: 10px;
            }

            .report-date {
              color: #909399;
              font-size: 14px;
            }
          }

          .report-section {
            margin-bottom: 30px;

            h3 {
              font-size: 20px;
              color: #303133;
              margin-bottom: 15px;
              padding-left: 10px;
              border-left: 4px solid #409eff;
            }

            .house-detail-item {
              margin-bottom: 20px;
              padding: 15px;
              background: #f5f7fa;
              border-radius: 8px;

              h4 {
                font-size: 16px;
                color: #303133;
                margin-bottom: 15px;
              }

              p {
                margin: 8px 0;
                color: #606266;
                line-height: 1.8;

                strong {
                  color: #303133;
                  margin-right: 8px;
                }
              }
            }
          }
        }
      }
    }
  }
}
</style>

