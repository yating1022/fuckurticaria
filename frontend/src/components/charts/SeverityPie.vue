<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useBreakpoint } from '../../composables/useBreakpoint'

use([PieChart, TooltipComponent, LegendComponent, CanvasRenderer])

interface Slice {
  severity: number
  label: string
  count: number
}

const props = defineProps<{ data: Slice[]; total: number }>()
const { isMobile } = useBreakpoint()

const COLORS: Record<number, string> = {
  1: '#4ade80',
  2: '#facc15',
  3: '#fb923c',
  4: '#f87171',
  5: '#dc2626',
}

const option = computed(() => ({
  tooltip: {
    backgroundColor: '#fdfbf7',
    borderColor: '#2d2d2d',
    borderWidth: 2,
    textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d' },
    formatter: (p: any) => `${p.name}: ${p.value} 次 (${p.percent}%)`,
  },
  legend: {
    bottom: 0,
    textStyle: { fontFamily: 'Patrick Hand', color: '#2d2d2d', fontSize: isMobile.value ? 11 : 14 },
  },
  series: [
    {
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', isMobile.value ? '40%' : '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: '#2d2d2d', borderWidth: 2, borderRadius: 4 },
      label: {
        fontFamily: 'Patrick Hand',
        fontSize: isMobile.value ? 11 : 14,
        color: '#2d2d2d',
      },
      data: props.data.map((s) => ({
        name: s.label,
        value: s.count,
        itemStyle: { color: COLORS[s.severity] ?? '#e5e0d8' },
      })),
    },
  ],
}))
</script>

<template>
  <VChart v-if="total > 0" :option="option" autoresize style="height: 280px" />
  <p v-else class="font-hand text-lg text-[#2d2d2d]/40 text-center py-16">
    暂无数据
  </p>
</template>
