<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, MarkAreaComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useBreakpoint } from '../../composables/useBreakpoint'

use([LineChart, GridComponent, TooltipComponent, MarkAreaComponent, CanvasRenderer])

interface Point {
  week_start: string
  week_end: string
  uas7_score: number
  level: string
  color: string
}

const props = defineProps<{ data: Point[] }>()
const { isMobile } = useBreakpoint()

const LEVEL_BANDS = [
  { top: 0, bottom: 0, color: 'rgba(74,222,128,0.10)', label: '无症状' },
  { top: 6, bottom: 0, color: 'rgba(250,204,21,0.10)', label: '轻度' },
  { top: 15, bottom: 6, color: 'rgba(251,146,60,0.10)', label: '中度' },
  { top: 27, bottom: 15, color: 'rgba(248,113,113,0.10)', label: '重度' },
  { top: 42, bottom: 27, color: 'rgba(220,38,38,0.10)', label: '极重度' },
]

const option = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#fdfbf7',
    borderColor: '#2d2d2d',
    borderWidth: 2,
    textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d' },
    formatter: (params: any) => {
      const p = params[0]
      const pt = props.data[p.dataIndex]
      return `<b>${pt.week_start} ~ ${pt.week_end}</b><br/>UAS7: ${p.value} (${pt.level})`
    },
  },
  grid: { left: isMobile.value ? 35 : 50, right: 15, top: 10, bottom: 30 },
  xAxis: {
    type: 'category',
    data: props.data.map((d) => d.week_start),
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', rotate: isMobile.value ? 60 : 30, fontSize: isMobile.value ? 10 : 11 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 42,
    axisLabel: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 10 : 12 },
    axisLine: { lineStyle: { color: '#2d2d2d', width: 2 } },
    splitLine: { lineStyle: { type: 'dashed', color: '#e5e0d8' } },
  },
  series: [
    {
      type: 'line',
      data: props.data.map((d) => d.uas7_score),
      smooth: 0.3,
      lineStyle: { width: 3, color: '#ff4d4d' },
      itemStyle: {
        color: (params: any) => props.data[params.dataIndex]?.color ?? '#ff4d4d',
        borderWidth: 2,
        borderColor: '#2d2d2d',
      },
      areaStyle: { color: 'rgba(255, 77, 77, 0.06)' },
      symbolSize: isMobile.value ? 6 : 8,
      markArea: {
        silent: true,
        data: LEVEL_BANDS.map((b) => [
          { yAxis: b.bottom, itemStyle: { color: b.color } },
          { yAxis: b.top },
        ]),
      },
    },
  ],
}))
</script>

<template>
  <VChart v-if="data.length" :option="option" autoresize style="height: 280px" />
  <p v-else class="font-hand text-lg text-[#2d2d2d]/40 text-center py-12">
    持续打卡后这里会显示趋势图
  </p>
</template>
