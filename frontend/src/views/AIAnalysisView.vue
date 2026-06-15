<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'

interface AIAnalysisResult {
  summary: string; trend: string; uas7_avg: number; uas7_level: string
  risk_factors: string[]; environment_correlation: string; lifestyle_correlation: string
  medication_effectiveness: string; suggestions: string[]; high_risk_days: string[]
}
interface TriggerPattern { cycle_type: string; cycle_description: string; avg_interval_days: number | null; confidence: string }
interface HighRiskWindow { start_date: string; end_date: string; risk_level: string; reason: string }
interface TriggerAnalysisResult {
  summary: string; patterns: TriggerPattern[]; trigger_factors: string[]
  high_risk_windows: HighRiskWindow[]; medication_correlation: string; environment_correlation: string; suggestions: string[]
}
interface AIInsightOut {
  id: number; user_id: number; insight_type: string
  content: AIAnalysisResult | TriggerAnalysisResult
  analysis_range_start: string | null; analysis_range_end: string | null
  model_version: string | null; created_at: string
}

type Tab = 'health' | 'trigger'
const tab = ref<Tab>('health')

const days = ref(30)
const triggerDays = ref(60)
const { data: insightsRaw, loading, request: fetchInsights } = useApi<AIInsightOut[]>()
const { data: triggerInsightsRaw, request: fetchTriggerInsights } = useApi<AIInsightOut[]>()
const { loading: analyzing, request: analyzeReq } = useApi<AIInsightOut>()
const { loading: triggerAnalyzing, request: triggerAnalyzeReq } = useApi<AIInsightOut>()
const current = ref<AIInsightOut | null>(null)
const triggerCurrent = ref<AIInsightOut | null>(null)
const error = ref('')

const insights = computed(() => insightsRaw.value ?? [])
const triggerInsights = computed(() => triggerInsightsRaw.value ?? [])

const trendIcons: Record<string, string> = { '好转': '📈', '稳定': '➡️', '恶化': '📉' }
const trendColors: Record<string, string> = { '好转': '#4ade80', '稳定': '#facc15', '恶化': '#f87171' }
const riskColors: Record<string, string> = { '高': '#f87171', '中': '#fb923c', '低': '#facc15' }
const confidenceColors: Record<string, string> = { '高': '#4ade80', '中': '#facc15', '低': '#f87171' }

function isTrigger(r: AIInsightOut): r is AIInsightOut & { content: TriggerAnalysisResult } {
  return r.insight_type === 'trigger_analysis'
}
function isHealth(r: AIInsightOut): r is AIInsightOut & { content: AIAnalysisResult } {
  return r.insight_type === 'period_report'
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function analyze() {
  error.value = ''
  try {
    const res = await analyzeReq(`/ai/analyze?days=${days.value}`, { method: 'POST' })
    if (res) current.value = res
    await fetchInsights('/ai/insights?insight_type=period_report&limit=10')
  } catch (e: any) { error.value = e?.message || '分析失败' }
}

async function triggerAnalyze() {
  error.value = ''
  try {
    const res = await triggerAnalyzeReq(`/ai/trigger-analysis?days=${triggerDays.value}`, { method: 'POST' })
    if (res) triggerCurrent.value = res
    await fetchTriggerInsights('/ai/insights?insight_type=trigger_analysis&limit=10')
  } catch (e: any) { error.value = e?.message || '分析失败' }
}

async function load() {
  await Promise.all([
    fetchInsights('/ai/insights?insight_type=period_report&limit=10'),
    fetchTriggerInsights('/ai/insights?insight_type=trigger_analysis&limit=10'),
  ])
  if (insights.value.length > 0) current.value = insights.value[0]
  if (triggerInsights.value.length > 0) triggerCurrent.value = triggerInsights.value[0]
}

onMounted(load)
</script>

<template>
  <div class="max-w-3xl mx-auto py-6 sm:py-10 px-4 sm:px-6">
    <div class="mb-8">
      <h2 class="font-marker text-2xl sm:text-4xl rotate-[-1deg]">AI 分析</h2>
      <p class="font-hand text-base text-[#2d2d2d]/50 mt-1">
        基于 DeepSeek 大模型，综合分析你的健康数据
      </p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-2 sm:gap-4 mb-8 border-b-2 border-[#2d2d2d]/20 pb-2 overflow-x-auto">
      <button
        v-for="t in (['health', 'trigger'] as Tab[])"
        :key="t"
        class="font-hand text-base sm:text-lg px-3 sm:px-4 py-2 transition-all whitespace-nowrap"
        :class="tab === t ? 'text-[#2d5da1] font-bold border-b-2 border-[#2d5da1] -mb-[2px]' : 'text-[#2d2d2d]/40 hover:text-[#2d2d2d]/70'"
        @click="tab = t; error = ''"
      >
        {{ t === 'health' ? '健康报告' : '触发周期分析' }}
      </button>
    </div>

    <div v-if="error" class="mb-6 border-2 border-[#ff4d4d] bg-[#ff4d4d]/5 p-4 font-hand text-[#ff4d4d]"
         :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
      {{ error }}
    </div>

    <!-- =============== Health Report Tab =============== -->
    <template v-if="tab === 'health'">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-end gap-3 mb-6">
        <select v-model="days"
          class="border-2 border-[#2d2d2d] bg-white px-3 py-2 font-hand text-sm"
          :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
          <option :value="7">近 7 天</option>
          <option :value="14">近 14 天</option>
          <option :value="30">近 30 天</option>
          <option :value="60">近 60 天</option>
          <option :value="90">近 90 天</option>
        </select>
        <HandDrawnButton :disabled="analyzing" @click="analyze">
          {{ analyzing ? '分析中...' : '开始分析' }}
        </HandDrawnButton>
      </div>

      <div v-if="analyzing" class="font-hand text-xl text-[#2d2d2d]/40 text-center py-20">
        AI 正在分析你的健康数据，请稍候...
      </div>

      <template v-else-if="current && isHealth(current)">
        <HandDrawnCard decoration="tape" class="mb-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
            <div class="flex items-center gap-3">
              <span class="text-3xl sm:text-4xl">{{ trendIcons[current.content.trend] ?? '📊' }}</span>
              <div>
                <p class="font-marker text-xl sm:text-2xl">{{ current.content.trend }}</p>
                <p class="font-hand text-sm text-[#2d2d2d]/40">
                  {{ current.analysis_range_start }} ~ {{ current.analysis_range_end }}
                </p>
              </div>
            </div>
            <div class="text-left sm:text-right">
              <p class="font-hand text-sm text-[#2d2d2d]/50">UAS7 均分</p>
              <p class="font-marker text-2xl sm:text-3xl" :style="{ color: trendColors[current.content.trend] ?? '#2d2d2d' }">
                {{ current.content.uas7_avg.toFixed(1) }}
              </p>
              <p class="font-hand text-xs text-[#2d2d2d]/40">{{ current.content.uas7_level }}</p>
            </div>
          </div>
          <p class="font-hand text-lg text-[#2d2d2d]/80 leading-relaxed">{{ current.content.summary }}</p>
        </HandDrawnCard>

        <HandDrawnCard class="mb-6" v-if="current.content.risk_factors.length > 0">
          <h3 class="font-marker text-xl mb-3">风险因素</h3>
          <div class="flex flex-wrap gap-2">
            <span v-for="(f, i) in current.content.risk_factors" :key="i"
              class="inline-block px-3 py-1 border-2 border-[#ff4d4d] bg-[#ff4d4d]/5 font-hand text-sm text-[#ff4d4d]"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">{{ f }}</span>
          </div>
        </HandDrawnCard>

        <div class="grid md:grid-cols-2 gap-6 mb-6">
          <HandDrawnCard>
            <h3 class="font-marker text-xl mb-3">环境关联</h3>
            <p class="font-hand text-base text-[#2d2d2d]/80 leading-relaxed">{{ current.content.environment_correlation }}</p>
          </HandDrawnCard>
          <HandDrawnCard>
            <h3 class="font-marker text-xl mb-3">生活习惯关联</h3>
            <p class="font-hand text-base text-[#2d2d2d]/80 leading-relaxed">{{ current.content.lifestyle_correlation }}</p>
          </HandDrawnCard>
        </div>

        <HandDrawnCard class="mb-6">
          <h3 class="font-marker text-xl mb-3">用药效果</h3>
          <p class="font-hand text-base text-[#2d2d2d]/80 leading-relaxed">{{ current.content.medication_effectiveness }}</p>
        </HandDrawnCard>

        <HandDrawnCard class="mb-6" decoration="tack">
          <h3 class="font-marker text-xl mb-3">建议</h3>
          <ul class="space-y-2">
            <li v-for="(s, i) in current.content.suggestions" :key="i" class="flex items-start gap-3">
              <span class="font-marker text-lg text-[#2d5da1] mt-0.5">{{ i + 1 }}.</span>
              <span class="font-hand text-base text-[#2d2d2d]/80 leading-relaxed">{{ s }}</span>
            </li>
          </ul>
        </HandDrawnCard>

        <HandDrawnCard v-if="current.content.high_risk_days.length > 0" class="mb-6">
          <h3 class="font-marker text-xl mb-3">高风险日期</h3>
          <div class="flex flex-wrap gap-2">
            <span v-for="d in current.content.high_risk_days" :key="d"
              class="inline-block px-3 py-1 border-2 border-[#2d2d2d] bg-[#fff9c4] font-hand text-sm"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">{{ d }}</span>
          </div>
        </HandDrawnCard>
      </template>

      <div v-else-if="!loading" class="text-center py-20">
        <HandDrawnCard>
          <p class="font-hand text-xl text-[#2d2d2d]/50 mb-4">暂无健康报告</p>
          <HandDrawnButton @click="analyze">开始分析</HandDrawnButton>
        </HandDrawnCard>
      </div>

      <!-- Health history -->
      <div v-if="insights.length > 1" class="mt-8">
        <h3 class="font-marker text-xl mb-4">历史报告</h3>
        <div class="space-y-3">
          <div v-for="ins in insights" :key="ins.id"
            class="border-2 border-[#2d2d2d] bg-white p-4 cursor-pointer transition-transform hover:rotate-[-0.5deg]"
            :class="{ 'border-[#2d5da1] bg-[#2d5da1]/5': current?.id === ins.id }"
            :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
            @click="current = ins">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2" v-if="isHealth(ins)">
              <div class="flex items-center gap-3 min-w-0">
                <span class="text-xl shrink-0">{{ trendIcons[ins.content.trend] ?? '📊' }}</span>
                <div class="min-w-0">
                  <p class="font-hand text-base text-[#2d2d2d] truncate">{{ ins.content.summary }}</p>
                  <p class="font-hand text-xs text-[#2d2d2d]/40 mt-1">
                    {{ ins.analysis_range_start }} ~ {{ ins.analysis_range_end }} · UAS7 {{ ins.content.uas7_avg.toFixed(1) }}
                  </p>
                </div>
              </div>
              <span class="font-hand text-xs text-[#2d2d2d]/30 whitespace-nowrap shrink-0">{{ formatTime(ins.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- =============== Trigger Analysis Tab =============== -->
    <template v-if="tab === 'trigger'">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-end gap-3 mb-6">
        <select v-model="triggerDays"
          class="border-2 border-[#2d2d2d] bg-white px-3 py-2 font-hand text-sm"
          :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
          <option :value="30">近 30 天</option>
          <option :value="60">近 60 天</option>
          <option :value="90">近 90 天</option>
          <option :value="120">近 120 天</option>
          <option :value="180">近 180 天</option>
        </select>
        <HandDrawnButton :disabled="triggerAnalyzing" @click="triggerAnalyze">
          {{ triggerAnalyzing ? '分析中...' : '开始分析' }}
        </HandDrawnButton>
      </div>

      <div v-if="triggerAnalyzing" class="font-hand text-xl text-[#2d2d2d]/40 text-center py-20">
        AI 正在分析发病周期和触发模式，请稍候...
      </div>

      <template v-else-if="triggerCurrent && isTrigger(triggerCurrent)">
        <!-- Summary -->
        <HandDrawnCard decoration="tape" class="mb-6">
          <p class="font-hand text-sm text-[#2d2d2d]/40 mb-2">
            分析周期: {{ triggerCurrent.analysis_range_start }} ~ {{ triggerCurrent.analysis_range_end }}
          </p>
          <p class="font-hand text-lg text-[#2d2d2d]/80 leading-relaxed">{{ triggerCurrent.content.summary }}</p>
        </HandDrawnCard>

        <!-- Patterns -->
        <HandDrawnCard class="mb-6" v-if="triggerCurrent.content.patterns.length > 0">
          <h3 class="font-marker text-xl mb-4">发现的周期模式</h3>
          <div class="space-y-4">
            <div v-for="(p, i) in triggerCurrent.content.patterns" :key="i"
              class="border-2 border-[#2d2d2d]/30 p-4"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 mb-2">
                <span class="font-marker text-lg">{{ p.cycle_type }}</span>
                <span class="font-hand text-sm px-2 py-0.5 border-2"
                  :style="{ borderColor: confidenceColors[p.confidence] ?? '#e5e0d8', color: confidenceColors[p.confidence] ?? '#2d2d2d', borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
                  置信度: {{ p.confidence }}
                </span>
              </div>
              <p class="font-hand text-base text-[#2d2d2d]/80 leading-relaxed">{{ p.cycle_description }}</p>
              <p v-if="p.avg_interval_days" class="font-hand text-sm text-[#2d2d2d]/50 mt-1">
                平均间隔: {{ p.avg_interval_days }} 天
              </p>
            </div>
          </div>
        </HandDrawnCard>

        <!-- Trigger factors ranking -->
        <HandDrawnCard class="mb-6">
          <h3 class="font-marker text-xl mb-3">触发因素排名</h3>
          <div class="space-y-2">
            <div v-for="(f, i) in triggerCurrent.content.trigger_factors" :key="i"
              class="flex items-center gap-3">
              <span class="font-marker text-2xl w-8 text-center"
                :style="{ color: i === 0 ? '#ff4d4d' : i === 1 ? '#fb923c' : '#facc15' }">
                {{ i + 1 }}
              </span>
              <span class="font-hand text-base text-[#2d2d2d]/80 flex-1 py-2 border-b-2 border-[#2d2d2d]/10">
                {{ f }}
              </span>
            </div>
          </div>
        </HandDrawnCard>

        <!-- High risk windows -->
        <HandDrawnCard class="mb-6" decoration="tack">
          <h3 class="font-marker text-xl mb-4">高危窗口期预测</h3>
          <div v-if="triggerCurrent.content.high_risk_windows.length > 0" class="space-y-3">
            <div v-for="(w, i) in triggerCurrent.content.high_risk_windows" :key="i"
              class="border-2 p-4 flex items-start gap-4"
              :style="{
                borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px',
                borderColor: riskColors[w.risk_level] ?? '#e5e0d8',
                backgroundColor: (riskColors[w.risk_level] ?? '#e5e0d8') + '10'
              }">
              <div class="w-10 h-10 flex items-center justify-center border-2 text-white font-marker text-sm"
                :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px', backgroundColor: riskColors[w.risk_level] ?? '#e5e0d8', borderColor: riskColors[w.risk_level] ?? '#e5e0d8' }">
                {{ w.risk_level }}
              </div>
              <div class="flex-1">
                <p class="font-marker text-base mb-1">{{ w.start_date }} ~ {{ w.end_date }}</p>
                <p class="font-hand text-sm text-[#2d2d2d]/70 leading-relaxed">{{ w.reason }}</p>
              </div>
            </div>
          </div>
          <p v-else class="font-hand text-base text-[#2d2d2d]/40">暂未发现明确的高危窗口期</p>
        </HandDrawnCard>

        <!-- Correlations -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
          <HandDrawnCard>
            <h3 class="font-marker text-xl mb-3">用药关联</h3>
            <p class="font-hand text-base text-[#2d2d2d]/80 leading-relaxed">{{ triggerCurrent.content.medication_correlation }}</p>
          </HandDrawnCard>
          <HandDrawnCard>
            <h3 class="font-marker text-xl mb-3">环境关联</h3>
            <p class="font-hand text-base text-[#2d2d2d]/80 leading-relaxed">{{ triggerCurrent.content.environment_correlation }}</p>
          </HandDrawnCard>
        </div>

        <!-- Suggestions -->
        <HandDrawnCard class="mb-6">
          <h3 class="font-marker text-xl mb-3">针对性建议</h3>
          <ul class="space-y-2">
            <li v-for="(s, i) in triggerCurrent.content.suggestions" :key="i" class="flex items-start gap-3">
              <span class="font-marker text-lg text-[#2d5da1] mt-0.5">{{ i + 1 }}.</span>
              <span class="font-hand text-base text-[#2d2d2d]/80 leading-relaxed">{{ s }}</span>
            </li>
          </ul>
        </HandDrawnCard>
      </template>

      <div v-else-if="!loading" class="text-center py-20">
        <HandDrawnCard>
          <p class="font-hand text-xl text-[#2d2d2d]/50 mb-2">触发周期分析</p>
          <p class="font-hand text-base text-[#2d2d2d]/30 mb-4">
            分析你的发病规律，发现隐藏的触发周期，预测高危窗口期
          </p>
          <HandDrawnButton @click="triggerAnalyze">开始分析</HandDrawnButton>
        </HandDrawnCard>
      </div>

      <!-- Trigger history -->
      <div v-if="triggerInsights.length > 1" class="mt-8">
        <h3 class="font-marker text-xl mb-4">历史分析</h3>
        <div class="space-y-3">
          <div v-for="ins in triggerInsights" :key="ins.id"
            class="border-2 border-[#2d2d2d] bg-white p-4 cursor-pointer transition-transform hover:rotate-[-0.5deg]"
            :class="{ 'border-[#2d5da1] bg-[#2d5da1]/5': triggerCurrent?.id === ins.id }"
            :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
            @click="triggerCurrent = ins">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2" v-if="isTrigger(ins)">
              <div class="min-w-0">
                <p class="font-hand text-base text-[#2d2d2d]">{{ ins.content.summary }}</p>
                <p class="font-hand text-xs text-[#2d2d2d]/40 mt-1">
                  {{ ins.analysis_range_start }} ~ {{ ins.analysis_range_end }} · {{ ins.content.patterns.length }} 个模式
                </p>
              </div>
              <span class="font-hand text-xs text-[#2d2d2d]/30 whitespace-nowrap">{{ formatTime(ins.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
