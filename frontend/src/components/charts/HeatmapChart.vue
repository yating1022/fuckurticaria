<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { HeatmapChart as HeatmapSeries } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useBreakpoint } from '../../composables/useBreakpoint'

use([HeatmapSeries, GridComponent, TooltipComponent, VisualMapComponent, CanvasRenderer])

interface Cell {
  day: number
  hour: number
  value: number
}

const props = defineProps<{ data: Cell[] }>()
const { isMobile } = useBreakpoint()

const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)

const option = computed(() => {
  const maxVal = Math.max(1, ...props.data.map((c) => c.value))

  return {
    tooltip: {
      backgroundColor: '#fdfbf7',
      borderColor: '#2d2d2d',
      borderWidth: 2,
      textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d' },
      formatter: (p: any) => `${days[p.value[1]]} ${hours[p.value[0]]}<br/>发病 ${p.value[2]} 次`,
    },
    grid: { left: isMobile.value ? 40 : 60, right: 15, top: 10, bottom: 40 },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: { show: true },
      axisLabel: {
        fontFamily: 'Patrick Hand',
        color: '#2d2d2d',
        interval: isMobile.value ? 5 : 2,
        fontSize: isMobile.value ? 9 : 11,
      },
      axisLine: { lineStyle: { color: '#2d2d2d' } },
    },
    yAxis: {
      type: 'category',
      data: days,
      axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 10 : 12 },
      axisLine: { lineStyle: { color: '#2d2d2d' } },
    },
    visualMap: {
      min: 0,
      max: maxVal,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: { color: ['#fdfbf7', '#facc15', '#fb923c', '#ff4d4d'] },
      textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 10 : 12 },
    },
    series: [
      {
        type: 'heatmap',
        data: props.data.map((c) => [c.hour, c.day, c.value]),
        emphasis: { itemStyle: { shadowBlur: 6, shadowColor: 'rgba(0,0,0,0.2)' } },
        itemStyle: { borderColor: '#e5e0d8', borderWidth: 1, borderRadius: 2 },
      },
    ],
  }
})
</script>

<template>
  <VChart v-if="data.length" :option="option" autoresize style="height: 280px" />
  <p v-else class="font-hand text-lg text-[#2d2d2d]/40 text-center py-16">
    暂无数据，记录发病后这里会显示时间分布
  </p>
</template>
