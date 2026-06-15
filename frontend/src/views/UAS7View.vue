<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'
import UAS7TrendChart from '../components/charts/UAS7TrendChart.vue'

interface UAS7Score {
  id: number; score_date: string; wheal_score: number; itch_score: number; daily_score: number | null; notes: string | null
}
interface WeeklyResp {
  start_date: string; end_date: string; uas7_score: number; level: string; color: string; days_scored: number; daily_scores: UAS7Score[]
}
interface TrendResp { weeks: number; data: { week_start: string; week_end: string; uas7_score: number; level: string; color: string }[] }

const { data: todayScore, request: fetchToday } = useApi<UAS7Score>()
const { data: weekly, request: fetchWeekly } = useApi<WeeklyResp>()
const { data: trend, request: fetchTrend } = useApi<TrendResp>()
const { loading: submitting, request: submitReq } = useApi<UAS7Score>()
const { loading: deleting, request: deleteReq } = useApi() // 添加 delete 请求

const wheal = ref(0)
const itch = ref(0)
const submitted = ref(false)

// id > 0 means the score was manually recorded; id === 0 is the default "no symptoms" placeholder
const hasRealRecord = computed(() => (todayScore.value?.id ?? 0) > 0)

const dailyScore = computed(() => wheal.value + itch.value)

const levelInfo = computed(() => {
  const s = dailyScore.value
  if (s === 0) return { label: '无症状', color: '#4ade80' }
  if (s <= 2) return { label: '轻度', color: '#facc15' }
  if (s <= 4) return { label: '中度', color: '#fb923c' }
  return { label: '重度', color: '#f87171' }
})

const whealLabels = ['无', '轻度\n(<20个)', '中度\n(20-50个)', '重度\n(>50个)']
const itchLabels = ['无', '轻度', '中度', '重度']

function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

async function load() {
  const t = todayStr()
  await fetchToday(`/uas7?date=${t}`)
  await fetchWeekly(`/uas7/weekly?date=${t}`)
  await fetchTrend('/uas7/trend?weeks=12')
  if (hasRealRecord.value && todayScore.value) {
    wheal.value = todayScore.value.wheal_score
    itch.value = todayScore.value.itch_score
    submitted.value = true
  }
}

async function submit() {
  const result = await submitReq('/uas7', {
    method: 'POST',
    body: JSON.stringify({
      score_date: todayStr(),
      wheal_score: wheal.value,
      itch_score: itch.value,
    }),
  })
  if (result) {
    submitted.value = true
    await fetchToday(`/uas7?date=${todayStr()}`)
    await fetchWeekly(`/uas7/weekly?date=${todayStr()}`)
    await fetchTrend('/uas7/trend?weeks=12')
  }
}

async function deleteScore() {
  if (!confirm('确认删除今天的评分记录？删除后将恢复为默认 0 分（无症状）。')) return
  await deleteReq(`/uas7?date=${todayStr()}`, { method: 'DELETE' })
  submitted.value = false
  wheal.value = 0
  itch.value = 0
  await fetchToday(`/uas7?date=${todayStr()}`)
  await fetchWeekly(`/uas7/weekly?date=${todayStr()}`)
  await fetchTrend('/uas7/trend?weeks=12')
}

onMounted(load)
</script>

<template>
  <div class="max-w-4xl mx-auto py-6 sm:py-10 px-4 sm:px-6">
    <h2 class="font-marker text-2xl sm:text-4xl mb-2 rotate-[-1deg]">UAS7 症状评分</h2>
    <p class="font-hand text-base text-[#2d2d2d]/50 mb-8">
      每日记录风团和瘙痒程度，系统自动计算 UAS7 周度总分
    </p>

    <!-- Today's scoring -->
    <HandDrawnCard decoration="tack" class="mb-8">
      <h3 class="font-marker text-2xl mb-4">今日打卡</h3>

      <!-- Wheal slider -->
      <div class="mb-6">
        <label class="font-marker text-lg text-[#2d2d2d] block mb-2">风团评分</label>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <button
            v-for="n in 4" :key="n-1"
            type="button"
            class="py-3 sm:py-4 border-2 border-[#2d2d2d] font-hand text-sm leading-tight transition-all duration-100 cursor-pointer whitespace-pre-line"
            :class="wheal === n-1
              ? 'text-white shadow-[3px_3px_0px_0px_#2d2d2d]'
              : 'bg-white text-[#2d2d2d]'"
            :style="{
              borderRadius: '155px 15px 225px 15px / 15px 225px 15px 155px',
              backgroundColor: wheal === n-1 ? '#ff4d4d' : undefined,
            }"
            @click="wheal = n-1"
          >
            {{ whealLabels[n-1] }}
          </button>
        </div>
      </div>

      <!-- Itch slider -->
      <div class="mb-6">
        <label class="font-marker text-lg text-[#2d2d2d] block mb-2">瘙痒评分</label>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <button
            v-for="n in 4" :key="n-1"
            type="button"
            class="py-3 sm:py-4 border-2 border-[#2d2d2d] font-hand text-sm leading-tight transition-all duration-100 cursor-pointer"
            :class="itch === n-1
              ? 'text-white shadow-[3px_3px_0px_0px_#2d2d2d]'
              : 'bg-white text-[#2d2d2d]'"
            :style="{
              borderRadius: '155px 15px 225px 15px / 15px 225px 15px 155px',
              backgroundColor: itch === n-1 ? '#2d5da1' : undefined,
            }"
            @click="itch = n-1"
          >
            {{ itchLabels[n-1] }}
          </button>
        </div>
      </div>

      <!-- Preview -->
      <div class="flex items-center gap-4 mb-4">
        <div
          class="w-20 h-20 flex flex-col items-center justify-center border-2 border-[#2d2d2d]"
          :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px', backgroundColor: levelInfo.color }"
        >
          <span class="font-marker text-3xl text-white">{{ dailyScore }}</span>
        </div>
        <div>
          <p class="font-marker text-xl" :style="{ color: levelInfo.color }">{{ levelInfo.label }}</p>
          <p class="font-hand text-sm text-[#2d2d2d]/50">今日评分（0-6）</p>
        </div>
      </div>

      <div class="flex items-center gap-3 flex-wrap">
        <HandDrawnButton :disabled="submitting" @click="submit">
          {{ submitting ? '提交中...' : (submitted ? '更新评分' : '提交评分') }}
        </HandDrawnButton>
        <button
          v-if="hasRealRecord"
          type="button"
          :disabled="deleting"
          class="font-hand text-sm text-[#ff4d4d] hover:text-[#d43b3b] underline underline-offset-2 disabled:opacity-40"
          @click="deleteScore"
        >
          {{ deleting ? '删除中...' : '删除记录' }}
        </button>
        <span v-if="submitted && !submitting" class="font-hand text-sm text-[#4ade80]">✓ 已记录</span>
      </div>
    </HandDrawnCard>

    <!-- Weekly UAS7 -->
    <HandDrawnCard decoration="tape" class="mb-8">
      <h3 class="font-marker text-2xl mb-2">本周 UAS7</h3>
      <div v-if="weekly" class="flex flex-col sm:flex-row items-center gap-4">
        <div
          class="w-24 h-24 flex flex-col items-center justify-center border-2 border-[#2d2d2d]"
          :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px', backgroundColor: weekly.color }"
        >
          <span class="font-marker text-4xl text-white">{{ weekly.uas7_score }}</span>
          <span class="font-hand text-xs text-white/80">/42</span>
        </div>
        <div>
          <p class="font-marker text-xl" :style="{ color: weekly.color }">{{ weekly.level }}</p>
          <p class="font-hand text-sm text-[#2d2d2d]/50">
            {{ weekly.start_date }} ~ {{ weekly.end_date }}
          </p>
          <p class="font-hand text-sm text-[#2d2d2d]/50">
            手动记录 {{ weekly.days_scored }} 天，未记录日默认无症状（0分）
          </p>
        </div>
      </div>
      <p v-else class="font-hand text-lg text-[#2d2d2d]/40">加载中...</p>
    </HandDrawnCard>

    <!-- Trend Chart -->
    <HandDrawnCard class="mb-8">
      <h3 class="font-marker text-2xl mb-4">UAS7 趋势（近12周）</h3>
      <UAS7TrendChart v-if="trend?.data" :data="trend.data" />
      <p v-else class="font-hand text-lg text-[#2d2d2d]/40 text-center py-12">
        持续打卡后这里会显示趋势图
      </p>
    </HandDrawnCard>
  </div>
</template>
