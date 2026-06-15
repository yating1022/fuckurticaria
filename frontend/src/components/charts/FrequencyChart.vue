<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useBreakpoint } from '../../composables/useBreakpoint'

use([LineChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer])

interface Point {
  date: string
  count: number
  avg_severity: number | null
}

const props = defineProps<{ data: Point[] }>()
const { isMobile } = useBreakpoint()

const option = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#fdfbf7',
    borderColor: '#2d2d2d',
    borderWidth: 2,
    textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d' },
    formatter: (params: any) => {
      const p = params[0]
      const sev = props.data[p.dataIndex]?.avg_severity
      return `<b>${p.name}</b><br/>发病次数: ${p.value}` +
        (sev != null ? `<br/>平均严重度: ${sev}` : '')
    },
  },
  grid: { left: isMobile.value ? 35 : 50, right: 15, top: 20, bottom: 60 },
  dataZoom: [
    { type: 'inside', start: 0, end: 100 },
    { type: 'slider', start: 0, end: 100, height: isMobile.value ? 28 : 20, bottom: 8,
      handleStyle: { borderColor: '#2d2d2d' }, textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: 10 } },
  ],
  xAxis: {
    type: 'category',
    data: props.data.map((d) => d.date),
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', rotate: isMobile.value ? 60 : 30, fontSize: isMobile.value ? 10 : 12 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 10 : 12 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
    splitLine: { lineStyle: { type: 'dashed', color: '#e5e0d8' } },
  },
  series: [
    {
      type: 'line',
      data: props.data.map((d) => d.count),
      smooth: 0.3,
      lineStyle: { width: 3, color: '#ff4d4d' },
      itemStyle: { color: '#ff4d4d', borderWidth: 2, borderColor: '#2d2d2d' },
      areaStyle: { color: 'rgba(255, 77, 77, 0.08)' },
      symbolSize: isMobile.value ? 6 : 8,
    },
  ],
}))
</script>

<template>
  <VChart v-if="data.length" :option="option" autoresize style="height: 300px" />
  <p v-else class="font-hand text-lg text-[#2d2d2d]/40 text-center py-16">
    暂无数据，记录发病后这里会显示趋势图
  </p>
</template>
