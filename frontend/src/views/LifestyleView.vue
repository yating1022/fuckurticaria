<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '../composables/useApi'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'

interface LifestyleLog {
  id: number; log_date: string
  sleep_hours: number | null; sleep_quality: number | null
  stress_level: number | null; exercise: boolean | null
  diet_tags: string[] | null; notes: string | null
}
interface CalendarDay { log_date: string; has_record: boolean }

const { data: record, request: fetchRecord } = useApi<LifestyleLog | null>()
const { data: calendar, request: fetchCalendar } = useApi<CalendarDay[]>()
const { loading: submitting, request: submitReq } = useApi<LifestyleLog>()

const selectedDate = ref(new Date().toISOString().slice(0, 10))
const calYear = ref(new Date().getFullYear())
const calMonth = ref(new Date().getMonth() + 1)

const sleepHours = ref(7)
const sleepQuality = ref(3)
const stressLevel = ref(3)
const exercise = ref(false)
const dietTags = ref<string[]>([])
const notes = ref('')

const ALL_TAGS = ['海鲜', '辛辣', '酒精', '牛奶', '鸡蛋', '坚果', '小麦', '高组胺食物', '加工食品', '咖啡', '其他']

const stressEmojis = [
  { value: 1, emoji: '😊', label: '很放松' },
  { value: 2, emoji: '😐', label: '一般' },
  { value: 3, emoji: '😟', label: '有点焦虑' },
  { value: 4, emoji: '😰', label: '压力大' },
  { value: 5, emoji: '😫', label: '崩溃' },
]

const encouragement = [
  '记录就是进步！', '坚持打卡，数据会说话！', '每天多了解自己一点',
  '你在认真对待自己的身体', '好习惯正在养成中！',
]

const showEncourage = ref(false)
const encourageText = ref('')

function randomEncourage() {
  encourageText.value = encouragement[Math.floor(Math.random() * encouragement.length)]
  showEncourage.value = true
  setTimeout(() => { showEncourage.value = false }, 3000)
}

function toggleTag(tag: string) {
  const i = dietTags.value.indexOf(tag)
  if (i >= 0) dietTags.value.splice(i, 1)
  else dietTags.value.push(tag)
}

async function loadRecord() {
  await fetchRecord(`/lifestyle?date=${selectedDate.value}`)
  if (record.value) {
    sleepHours.value = record.value.sleep_hours ?? 7
    sleepQuality.value = record.value.sleep_quality ?? 3
    stressLevel.value = record.value.stress_level ?? 3
    exercise.value = record.value.exercise ?? false
    dietTags.value = record.value.diet_tags ? [...record.value.diet_tags] : []
    notes.value = record.value.notes ?? ''
  } else {
    sleepHours.value = 7; sleepQuality.value = 3; stressLevel.value = 3
    exercise.value = false; dietTags.value = []; notes.value = ''
  }
}

async function loadCalendar() {
  await fetchCalendar(`/lifestyle/calendar?year=${calYear.value}&month=${calMonth.value}`)
}

function prevMonth() {
  if (calMonth.value === 1) { calYear.value--; calMonth.value = 12 }
  else calMonth.value--
  loadCalendar()
}
function nextMonth() {
  if (calMonth.value === 12) { calYear.value++; calMonth.value = 1 }
  else calMonth.value++
  loadCalendar()
}

function selectDay(d: string) {
  selectedDate.value = d
  loadRecord()
}

const monthDays = computed(() => {
  if (!calendar.value) return []
  const firstDow = new Date(calYear.value, calMonth.value - 1, 1).getDay()
  const offset = firstDow === 0 ? 6 : firstDow - 1 // Monday=0
  const blanks = Array.from({ length: offset }, () => null)
  return [...blanks, ...calendar.value]
})

async function submit() {
  await submitReq('/lifestyle', {
    method: 'POST',
    body: JSON.stringify({
      log_date: selectedDate.value,
      sleep_hours: sleepHours.value,
      sleep_quality: sleepQuality.value,
      stress_level: stressLevel.value,
      exercise: exercise.value,
      diet_tags: dietTags.value.length ? dietTags.value : null,
      notes: notes.value || null,
    }),
  })
  randomEncourage()
  await loadCalendar()
}

watch(selectedDate, loadRecord)
onMounted(() => { loadRecord(); loadCalendar() })
</script>

<template>
  <div class="max-w-4xl mx-auto py-6 sm:py-10 px-4 sm:px-6">
    <h2 class="font-marker text-2xl sm:text-4xl mb-2 rotate-[-1deg]">生活打卡</h2>
    <p class="font-hand text-base text-[#2d2d2d]/50 mb-8">
      记录睡眠、压力、运动和饮食，为 AI 分析积累数据
    </p>

    <div class="grid md:grid-cols-[280px_1fr] gap-8">
      <!-- Calendar -->
      <HandDrawnCard>
        <div class="flex items-center justify-between mb-3">
          <button class="font-hand text-lg cursor-pointer px-2 hover:text-[#ff4d4d]" @click="prevMonth">&lt;</button>
          <span class="font-marker text-lg">{{ calYear }}年{{ calMonth }}月</span>
          <button class="font-hand text-lg cursor-pointer px-2 hover:text-[#ff4d4d]" @click="nextMonth">&gt;</button>
        </div>
        <div class="grid grid-cols-7 gap-1 text-center mb-1">
          <span v-for="d in ['一','二','三','四','五','六','日']" :key="d"
                class="font-hand text-xs text-[#2d2d2d]/40">{{ d }}</span>
        </div>
        <div class="grid grid-cols-7 gap-1 text-center">
          <template v-for="(item, i) in monthDays" :key="i">
            <div v-if="!item" />
            <button
              v-else
              class="w-9 h-9 flex items-center justify-center font-hand text-sm border-2 cursor-pointer transition-all duration-100"
              :class="[
                item.log_date === selectedDate
                  ? 'border-[#ff4d4d] bg-[#ff4d4d] text-white'
                  : item.has_record
                    ? 'border-[#2d5da1] bg-[#2d5da1]/10 text-[#2d5da1]'
                    : 'border-transparent text-[#2d2d2d]/60 hover:border-[#e5e0d8]',
              ]"
              :style="{ borderRadius: '8px' }"
              @click="selectDay(item.log_date)"
            >
              {{ parseInt(item.log_date.split('-')[2]) }}
            </button>
          </template>
        </div>
        <div class="flex gap-3 mt-3 font-hand text-xs text-[#2d2d2d]/40">
          <span class="flex items-center gap-1"><span class="w-3 h-3 bg-[#ff4d4d] rounded-sm inline-block" /> 今天</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 bg-[#2d5da1]/20 border border-[#2d5da1] rounded-sm inline-block" /> 已打卡</span>
        </div>
      </HandDrawnCard>

      <!-- Form -->
      <div>
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 mb-4">
          <h3 class="font-marker text-2xl">{{ selectedDate }} 打卡</h3>
          <span v-if="showEncourage" class="font-hand text-[#4ade80] text-sm animate-pulse">
            {{ encourageText }}
          </span>
        </div>

        <HandDrawnCard decoration="tack" class="mb-6">
          <div class="flex flex-col gap-6">
            <!-- Sleep hours -->
            <div>
              <label class="font-marker text-lg text-[#2d2d2d] block mb-2">睡眠时长</label>
              <div class="flex items-center gap-4">
                <input type="range" v-model.number="sleepHours" min="0" max="14" step="0.5"
                       class="flex-1 accent-[#2d5da1] h-2" />
                <span class="font-marker text-2xl w-16 text-right" style="color: #2d5da1">{{ sleepHours }}h</span>
              </div>
            </div>

            <!-- Sleep quality -->
            <div>
              <label class="font-marker text-lg text-[#2d2d2d] block mb-2">睡眠质量</label>
              <div class="flex gap-2">
                <button
                  v-for="n in 5" :key="n"
                  class="text-3xl cursor-pointer transition-transform duration-100"
                  :class="n <= sleepQuality ? 'scale-110' : 'opacity-30 grayscale'"
                  @click="sleepQuality = n"
                >⭐</button>
              </div>
            </div>

            <!-- Stress level -->
            <div>
              <label class="font-marker text-lg text-[#2d2d2d] block mb-2">压力水平</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="s in stressEmojis" :key="s.value"
                  class="flex flex-col items-center gap-1 px-3 py-2 border-2 cursor-pointer transition-all duration-100"
                  :class="stressLevel === s.value
                    ? 'border-[#ff4d4d] bg-[#ff4d4d]/10 shadow-[2px_2px_0px_0px_#2d2d2d]'
                    : 'border-[#e5e0d8] hover:border-[#2d2d2d]'"
                  :style="{ borderRadius: '155px 15px 225px 15px / 15px 225px 15px 155px' }"
                  @click="stressLevel = s.value"
                >
                  <span class="text-2xl">{{ s.emoji }}</span>
                  <span class="font-hand text-xs text-[#2d2d2d]/60">{{ s.label }}</span>
                </button>
              </div>
            </div>

            <!-- Exercise toggle -->
            <div>
              <label class="font-marker text-lg text-[#2d2d2d] block mb-2">今日运动</label>
              <button
                class="px-6 py-3 border-2 border-[#2d2d2d] font-hand text-lg cursor-pointer transition-all duration-100"
                :class="exercise
                  ? 'bg-[#4ade80] text-white shadow-[3px_3px_0px_0px_#2d2d2d]'
                  : 'bg-white text-[#2d2d2d]'"
                :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
                @click="exercise = !exercise"
              >
                {{ exercise ? '✓ 有运动' : '无运动' }}
              </button>
            </div>

            <!-- Diet tags -->
            <div>
              <label class="font-marker text-lg text-[#2d2d2d] block mb-2">饮食标签</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="tag in ALL_TAGS" :key="tag"
                  class="px-3 py-1.5 border-2 border-[#2d2d2d] font-hand text-sm cursor-pointer transition-all duration-100"
                  :class="dietTags.includes(tag)
                    ? 'bg-[#fff9c4] text-[#2d2d2d] shadow-[2px_2px_0px_0px_#2d2d2d]'
                    : 'bg-white text-[#2d2d2d]/60'"
                  :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
                  @click="toggleTag(tag)"
                >
                  {{ tag }}
                </button>
              </div>
            </div>

            <!-- Notes -->
            <div>
              <label class="font-marker text-lg text-[#2d2d2d] block mb-1">备注</label>
              <textarea
                v-model="notes"
                rows="2"
                placeholder="补充说明..."
                class="w-full border-2 border-[#2d2d2d] bg-white px-4 py-3 font-hand text-base
                       placeholder:text-[#2d2d2d]/30
                       focus:border-[#2d5da1] focus:ring-2 focus:ring-[#2d5da1]/20 focus:outline-none"
                :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
              />
            </div>

            <HandDrawnButton :disabled="submitting" @click="submit">
              {{ submitting ? '保存中...' : (record ? '更新打卡' : '打卡') }}
            </HandDrawnButton>
          </div>
        </HandDrawnCard>
      </div>
    </div>
  </div>
</template>
