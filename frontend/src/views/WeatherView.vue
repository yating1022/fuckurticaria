<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'
import WeatherTrendChart from '../components/charts/WeatherTrendChart.vue'

interface WeatherSnap {
  id: number; snapshot_at: string
  temperature: number | null; humidity: number | null; pressure: number | null
  pollen_index: number | null; aqi: number | null
  aqi_category: string | null; aqi_primary: string | null
  pm25: number | null; pm10: number | null
  no2: number | null; so2: number | null; co: number | null; o3: number | null
  weather_desc: string | null; city: string | null
}
interface CityInfo { city: string; location_id: string }

const { data: current, loading, request: fetchCurrent } = useApi<WeatherSnap | null>()
const { data: city, request: fetchCity } = useApi<CityInfo>()
const { loading: refreshing, request: refreshReq } = useApi<WeatherSnap | null>()

const { data: historyRaw, loading: historyLoading, request: fetchHistory } = useApi<WeatherSnap[]>()
const history = computed(() => historyRaw.value ?? [])
const trendDays = ref(7)
const trendOptions = [3, 7, 14, 30]

async function loadHistory() {
  await fetchHistory(`/weather/history?days=${trendDays.value}`)
}

const weatherIcons: Record<string, string> = {
  '晴': '☀️', '多云': '⛅', '阴': '☁️', '小雨': '🌦️', '中雨': '🌧️',
  '大雨': '⛈️', '雷阵雨': '⛈️', '雪': '🌨️', '雾': '🌫️', '霾': '😷',
}

function aqiLevel(aqi: number | null) {
  if (!aqi) return { label: '--', color: '#e5e0d8' }
  if (aqi <= 50) return { label: '优', color: '#4ade80' }
  if (aqi <= 100) return { label: '良', color: '#facc15' }
  if (aqi <= 150) return { label: '轻度', color: '#fb923c' }
  return { label: '污染', color: '#f87171' }
}

function pollenLevel(idx: number | null) {
  if (!idx) return { label: '--', color: '#e5e0d8' }
  if (idx <= 1) return { label: '低', color: '#4ade80' }
  if (idx <= 3) return { label: '中', color: '#facc15' }
  return { label: '高', color: '#f87171' }
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function refresh() {
  await refreshReq('/weather/refresh', { method: 'POST' })
  await fetchCurrent('/weather/current')
}

async function load() {
  await fetchCity('/weather/city')
  await fetchCurrent('/weather/current')
  await loadHistory()
}

onMounted(load)
</script>

<template>
  <div class="max-w-3xl mx-auto py-6 sm:py-10 px-4 sm:px-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-8">
      <div>
        <h2 class="font-marker text-2xl sm:text-4xl rotate-[-1deg]">环境数据</h2>
        <p class="font-hand text-base text-[#2d2d2d]/50 mt-1">
          {{ city?.city ?? '未配置' }} — 自动抓取天气、花粉和空气质量
        </p>
      </div>
      <HandDrawnButton :disabled="refreshing" @click="refresh">
        {{ refreshing ? '刷新中...' : '立即刷新' }}
      </HandDrawnButton>
    </div>

    <div v-if="loading" class="font-hand text-xl text-[#2d2d2d]/40 text-center py-20">加载中...</div>

    <template v-else-if="current">
      <!-- Main weather card -->
      <HandDrawnCard decoration="tape" class="mb-8">
        <div class="flex items-center gap-6">
          <span class="text-7xl">{{ weatherIcons[current.weather_desc ?? ''] ?? '🌡️' }}</span>
          <div>
            <p class="font-marker text-5xl" style="color: #2d2d2d">
              {{ current.temperature ?? '--' }}<span class="text-2xl">°C</span>
            </p>
            <p class="font-hand text-xl text-[#2d2d2d]/70">{{ current.weather_desc ?? '--' }}</p>
            <p class="font-hand text-sm text-[#2d2d2d]/40 mt-1">
              更新于 {{ formatTime(current.snapshot_at) }}
            </p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mt-6">
          <!-- Humidity -->
          <div class="border-2 border-[#2d2d2d] p-4 text-center"
               :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
            <p class="font-hand text-sm text-[#2d2d2d]/50">湿度</p>
            <p class="font-marker text-3xl" style="color: #2d5da1">{{ current.humidity ?? '--' }}%</p>
          </div>
          <!-- Pressure -->
          <div class="border-2 border-[#2d2d2d] p-4 text-center"
               :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
            <p class="font-hand text-sm text-[#2d2d2d]/50">气压</p>
            <p class="font-marker text-3xl" style="color: #2d2d2d">{{ current.pressure ?? '--' }}<span class="text-lg">hPa</span></p>
          </div>
        </div>
      </HandDrawnCard>

      <!-- AQI & Pollen -->
      <div class="grid md:grid-cols-2 gap-6 mb-8">
        <HandDrawnCard>
          <h3 class="font-marker text-xl mb-3">空气质量 (AQI)</h3>
          <div class="flex items-center gap-4 mb-4">
            <div
              class="w-16 h-16 flex items-center justify-center border-2 border-[#2d2d2d]"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px', backgroundColor: aqiLevel(current.aqi).color }"
            >
              <span class="font-marker text-2xl text-white">{{ current.aqi ?? '--' }}</span>
            </div>
            <div>
              <p class="font-hand text-lg" :style="{ color: aqiLevel(current.aqi).color }">
                {{ current.aqi_category ?? aqiLevel(current.aqi).label }}
              </p>
              <p v-if="current.aqi_primary" class="font-hand text-sm text-[#2d2d2d]/40">
                主要污染物: {{ current.aqi_primary }}
              </p>
            </div>
          </div>
          <!-- Pollutant breakdown -->
          <div v-if="current.pm25 != null" class="grid grid-cols-3 gap-2">
            <div v-for="p in [
              { label: 'PM2.5', value: current.pm25, unit: 'μg/m³' },
              { label: 'PM10', value: current.pm10, unit: 'μg/m³' },
              { label: 'NO₂', value: current.no2, unit: 'μg/m³' },
              { label: 'SO₂', value: current.so2, unit: 'μg/m³' },
              { label: 'CO', value: current.co, unit: 'mg/m³' },
              { label: 'O₃', value: current.o3, unit: 'μg/m³' },
            ]" :key="p.label"
              class="text-center border-2 border-[#2d2d2d]/20 py-2 px-1"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
              <p class="font-hand text-xs text-[#2d2d2d]/50">{{ p.label }}</p>
              <p class="font-marker text-base">{{ p.value ?? '--' }}</p>
              <p class="font-hand text-xs text-[#2d2d2d]/30">{{ p.unit }}</p>
            </div>
          </div>
        </HandDrawnCard>

        <HandDrawnCard>
          <h3 class="font-marker text-xl mb-3">花粉指数</h3>
          <div class="flex items-center gap-4">
            <div
              class="w-16 h-16 flex items-center justify-center border-2 border-[#2d2d2d]"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px', backgroundColor: pollenLevel(current.pollen_index).color }"
            >
              <span class="font-marker text-2xl text-white">{{ current.pollen_index ?? '--' }}</span>
            </div>
            <div>
              <p class="font-hand text-lg" :style="{ color: pollenLevel(current.pollen_index).color }">
                {{ pollenLevel(current.pollen_index).label }}
              </p>
              <p class="font-hand text-sm text-[#2d2d2d]/40">
                {{ current.pollen_index != null ? '等级 ' + current.pollen_index : '暂无数据' }}
              </p>
            </div>
          </div>
        </HandDrawnCard>
      </div>

      <!-- History Trend -->
      <HandDrawnCard decoration="tack" class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-marker text-2xl">历史趋势</h3>
          <div class="flex gap-2">
            <button
              v-for="d in trendOptions" :key="d"
              type="button"
              class="px-3 py-1 border-2 border-[#2d2d2d] font-hand text-sm cursor-pointer transition-all"
              :class="trendDays === d
                ? 'bg-[#2d5da1] text-white shadow-[3px_3px_0px_0px_#2d2d2d]'
                : 'bg-white text-[#2d2d2d]'"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
              @click="trendDays = d; loadHistory()"
            >
              {{ d }}天
            </button>
          </div>
        </div>
        <div v-if="historyLoading" class="font-hand text-lg text-[#2d2d2d]/40 text-center py-12">加载中...</div>
        <WeatherTrendChart v-else :data="history" />
      </HandDrawnCard>
    </template>

    <div v-else class="text-center py-20">
      <HandDrawnCard>
        <p class="font-hand text-xl text-[#2d2d2d]/50 mb-4">暂无天气数据</p>
        <HandDrawnButton @click="refresh">立即抓取</HandDrawnButton>
      </HandDrawnCard>
    </div>
  </div>
</template>
