<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useApi } from '../composables/useApi'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import FrequencyChart from '../components/charts/FrequencyChart.vue'
import HeatmapChart from '../components/charts/HeatmapChart.vue'
import SeverityPie from '../components/charts/SeverityPie.vue'

interface FreqResp {
  granularity: string
  data: { date: string; count: number; avg_severity: number | null }[]
}
interface HeatResp {
  data: { day: number; hour: number; value: number }[]
}
interface SevResp {
  total: number
  data: { severity: number; label: string; count: number }[]
}

const { data: freqData, loading: freqLoading, request: fetchFreq } = useApi<FreqResp>()
const { data: heatData, loading: heatLoading, request: fetchHeat } = useApi<HeatResp>()
const { data: sevData, loading: sevLoading, request: fetchSev } = useApi<SevResp>()

const granularity = ref<'day' | 'week' | 'month'>('week')

function loadAll() {
  fetchFreq(`/stats/outbreak-frequency?granularity=${granularity.value}`)
  fetchHeat('/stats/outbreak-heatmap')
  fetchSev('/stats/severity-distribution')
}

watch(granularity, () => {
  fetchFreq(`/stats/outbreak-frequency?granularity=${granularity.value}`)
})

onMounted(loadAll)

const graOptions = [
  { value: 'day' as const, label: '按日' },
  { value: 'week' as const, label: '按周' },
  { value: 'month' as const, label: '按月' },
]
</script>

<template>
  <div class="max-w-4xl mx-auto py-6 sm:py-10 px-4 sm:px-6">
    <h2 class="font-marker text-2xl sm:text-4xl mb-8 rotate-[-1deg]">发病趋势</h2>

    <!-- 频率趋势图 -->
    <HandDrawnCard decoration="tape" class="mb-8">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
        <h3 class="font-marker text-2xl">发病频率</h3>
        <div class="flex gap-2">
          <button
            v-for="opt in graOptions"
            :key="opt.value"
            class="px-3 py-1 border-2 border-[#2d2d2d] font-hand text-sm transition-all duration-100 cursor-pointer"
            :class="granularity === opt.value
              ? 'bg-[#ff4d4d] text-white'
              : 'bg-white text-[#2d2d2d]'"
            :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
            @click="granularity = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
      <div v-if="freqLoading" class="font-hand text-center py-12 text-[#2d2d2d]/40">加载中...</div>
      <FrequencyChart v-else :data="freqData?.data ?? []" />
    </HandDrawnCard>

    <!-- 热力图 -->
    <HandDrawnCard decoration="tack" class="mb-8">
      <h3 class="font-marker text-2xl mb-4">时间分布</h3>
      <p class="font-hand text-sm text-[#2d2d2d]/50 mb-2">
        颜色越深代表该时段发病越频繁，帮你发现隐藏的发作规律
      </p>
      <div v-if="heatLoading" class="font-hand text-center py-12 text-[#2d2d2d]/40">加载中...</div>
      <HeatmapChart v-else :data="heatData?.data ?? []" />
    </HandDrawnCard>

    <!-- 严重程度分布 -->
    <HandDrawnCard class="mb-8">
      <h3 class="font-marker text-2xl mb-4">严重程度分布</h3>
      <div v-if="sevLoading" class="font-hand text-center py-12 text-[#2d2d2d]/40">加载中...</div>
      <SeverityPie v-else :data="sevData?.data ?? []" :total="sevData?.total ?? 0" />
    </HandDrawnCard>
  </div>
</template>
