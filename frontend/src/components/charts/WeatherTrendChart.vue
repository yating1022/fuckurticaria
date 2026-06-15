<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useBreakpoint } from '../../composables/useBreakpoint'

use([LineChart, BarChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer])

interface Snap {
  id: number; snapshot_at: string
  temperature: number | null; humidity: number | null; pressure: number | null
  pollen_index: number | null; aqi: number | null
  weather_desc: string | null; city: string | null
}

const props = defineProps<{ data: Snap[] }>()
const { isMobile } = useBreakpoint()

const timeLabels = computed(() =>
  props.data.map((d) => {
    const dt = new Date(d.snapshot_at)
    if (isMobile.value) {
      return `${dt.getMonth() + 1}/${dt.getDate()}\n${String(dt.getHours()).padStart(2, '0')}:00`
    }
    return `${dt.getMonth() + 1}/${dt.getDate()} ${String(dt.getHours()).padStart(2, '0')}:00`
  })
)

const sharedAxis = () => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#fdfbf7',
    borderColor: '#2d2d2d',
    borderWidth: 2,
    textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 11 : 12 },
  },
  grid: { left: isMobile.value ? 35 : 45, right: 10, top: 10, bottom: 45 },
  dataZoom: [
    { type: 'inside', start: 0, end: 100 },
    { type: 'slider', height: isMobile.value ? 26 : 18, bottom: 2, borderColor: '#2d2d2d', fillerColor: 'rgba(45,93,161,0.12)',
      handleStyle: { borderColor: '#2d2d2d' }, textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: 10 } },
  ],
  xAxis: {
    type: 'category',
    data: timeLabels.value,
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', rotate: isMobile.value ? 0 : 45, fontSize: isMobile.value ? 9 : 10, interval: isMobile.value ? 'auto' : 0 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
  },
})

const tempOption = computed(() => ({
  ...sharedAxis(),
  yAxis: {
    type: 'value', name: '°C',
    nameTextStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d' },
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 10 : 12 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
    splitLine: { lineStyle: { type: 'dashed', color: '#e5e0d8' } },
  },
  series: [{
    type: 'line', smooth: 0.3,
    data: props.data.map((d) => d.temperature),
    lineStyle: { width: 3, color: '#ff4d4d' },
    itemStyle: { color: '#ff4d4d', borderWidth: 2, borderColor: '#2d2d2d' },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
      { offset: 0, color: 'rgba(255,77,77,0.15)' }, { offset: 1, color: 'rgba(255,77,77,0)' },
    ]}},
    symbolSize: 6,
  }],
}))

const humidityOption = computed(() => ({
  ...sharedAxis(),
  yAxis: {
    type: 'value', name: '%', min: 0, max: 100,
    nameTextStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d' },
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 10 : 12 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
    splitLine: { lineStyle: { type: 'dashed', color: '#e5e0d8' } },
  },
  series: [{
    type: 'line', smooth: 0.3,
    data: props.data.map((d) => d.humidity),
    lineStyle: { width: 3, color: '#2d5da1' },
    itemStyle: { color: '#2d5da1', borderWidth: 2, borderColor: '#2d2d2d' },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
      { offset: 0, color: 'rgba(45,93,161,0.15)' }, { offset: 1, color: 'rgba(45,93,161,0)' },
    ]}},
    symbolSize: 6,
  }],
}))

const aqiColors = ['#4ade80', '#facc15', '#fb923c', '#f87171', '#9333ea', '#7f1d1d']

function aqiColor(val: number | null) {
  if (val == null) return '#e5e0d8'
  if (val <= 50) return aqiColors[0]
  if (val <= 100) return aqiColors[1]
  if (val <= 150) return aqiColors[2]
  if (val <= 200) return aqiColors[3]
  if (val <= 300) return aqiColors[4]
  return aqiColors[5]
}

const aqiOption = computed(() => ({
  ...sharedAxis(),
  yAxis: {
    type: 'value', name: 'AQI',
    nameTextStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d' },
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 10 : 12 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
    splitLine: { lineStyle: { type: 'dashed', color: '#e5e0d8' } },
  },
  series: [{
    type: 'bar',
    data: props.data.map((d) => ({
      value: d.aqi,
      itemStyle: { color: aqiColor(d.aqi), borderColor: '#2d2d2d', borderWidth: 1 },
    })),
    barMaxWidth: 20,
  }],
}))

const pollenOption = computed(() => ({
  ...sharedAxis(),
  yAxis: {
    type: 'value', name: '等级', min: 0,
    nameTextStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d' },
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 10 : 12 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
    splitLine: { lineStyle: { type: 'dashed', color: '#e5e0d8' } },
  },
  series: [{
    type: 'line', smooth: 0.3,
    data: props.data.map((d) => d.pollen_index),
    lineStyle: { width: 3, color: '#f59e0b' },
    itemStyle: { color: '#f59e0b', borderWidth: 2, borderColor: '#2d2d2d' },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
      { offset: 0, color: 'rgba(245,158,11,0.15)' }, { offset: 1, color: 'rgba(245,158,11,0)' },
    ]}},
    symbolSize: 6,
  }],
}))
</script>

<template>
  <div v-if="data.length" class="grid md:grid-cols-2 gap-4">
    <div class="border-2 border-[#2d2d2d] bg-white p-3"
         :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
      <p class="font-marker text-base text-[#2d2d2d] mb-1">温度趋势</p>
      <VChart :option="tempOption" autoresize style="height: 240px" />
    </div>
    <div class="border-2 border-[#2d2d2d] bg-white p-3"
         :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
      <p class="font-marker text-base text-[#2d2d2d] mb-1">湿度趋势</p>
      <VChart :option="humidityOption" autoresize style="height: 240px" />
    </div>
    <div class="border-2 border-[#2d2d2d] bg-white p-3"
         :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
      <p class="font-marker text-base text-[#2d2d2d] mb-1">AQI 空气质量</p>
      <VChart :option="aqiOption" autoresize style="height: 240px" />
    </div>
    <div class="border-2 border-[#2d2d2d] bg-white p-3"
         :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
      <p class="font-marker text-base text-[#2d2d2d] mb-1">花粉指数</p>
      <VChart :option="pollenOption" autoresize style="height: 240px" />
    </div>
  </div>
  <p v-else class="font-hand text-lg text-[#2d2d2d]/40 text-center py-12">
    暂无历史环境数据
  </p>
</template>
