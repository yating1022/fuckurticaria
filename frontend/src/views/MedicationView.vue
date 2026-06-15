<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'
import HandDrawnInput from '../components/ui/HandDrawnInput.vue'
import type { Medication, MedicationRecord } from '../types/medication'

// --- Medications ---
const { data: medications, request: fetchMeds } = useApi<Medication[]>()
const { request: createMed } = useApi<Medication>()
const { request: deleteMed } = useApi<{ detail: string }>()

// --- Records ---
const { data: records, request: fetchRecords } = useApi<MedicationRecord[]>()
const { request: createRecord } = useApi<MedicationRecord>()
const { request: deleteRecord } = useApi<{ detail: string }>()
const { loading: submitting } = useApi()

// --- Quick log form ---
const selectedMedId = ref<number | null>(null)
const dose = ref('')
const takenAt = ref(new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Shanghai' }).replace(' ', 'T').slice(0, 16))
const isPrn = ref(false)
const effectiveness = ref<number | null>(null)
const sideEffects = ref<string[]>([])
const feedbackNote = ref('')

const showFeedback = ref(false)
const sideEffectOptions = ['嗜睡', '口干', '头晕', '恶心', '头痛', '心悸', '皮疹加重', '其他']

const selectedMed = computed(() =>
  medications.value?.find((m) => m.id === selectedMedId.value) ?? null
)

const groupedMeds = computed(() => {
  if (!medications.value) return {}
  const groups: Record<string, Medication[]> = {}
  for (const m of medications.value) {
    const cat = m.category ?? '未分类'
    ;(groups[cat] ??= []).push(m)
  }
  return groups
})

// --- New medication form ---
const showAddForm = ref(false)
const newMed = ref({ name: '', category: '', default_dose: '' })

// --- Feedback edit modal ---
const showFeedbackModal = ref(false)
const editingRecordId = ref<number | null>(null)
const fbEffectiveness = ref<number | null>(null)
const fbSideEffects = ref<string[]>([])
const fbNote = ref('')
const fbSaving = ref(false)

const effectivenessLabels = ['', '无效', '效果差', '一般', '有效', '非常有效']
const effectivenessColors = ['', '#f87171', '#fb923c', '#facc15', '#4ade80', '#22d3ee']

async function load() {
  await fetchMeds('/medications')
  await fetchRecords('/medication-records')
  if (medications.value?.length && !selectedMedId.value) {
    selectedMedId.value = medications.value[0].id
    dose.value = medications.value[0].default_dose ?? ''
  }
}

function selectMed(med: Medication) {
  selectedMedId.value = med.id
  dose.value = med.default_dose ?? ''
}

function toggleSideEffect(se: string) {
  const idx = sideEffects.value.indexOf(se)
  if (idx >= 0) sideEffects.value.splice(idx, 1)
  else sideEffects.value.push(se)
}

async function quickLog() {
  if (!selectedMedId.value || !dose.value) return
  await createRecord('/medication-records', {
    method: 'POST',
    body: JSON.stringify({
      medication_id: selectedMedId.value,
      dose: dose.value,
      taken_at: new Date(takenAt.value).toISOString(),
      is_prn: isPrn.value,
      effectiveness: effectiveness.value,
      side_effects: sideEffects.value.length > 0 ? sideEffects.value : null,
      feedback_note: feedbackNote.value || null,
    }),
  })
  // Reset feedback
  effectiveness.value = null
  sideEffects.value = []
  feedbackNote.value = ''
  showFeedback.value = false
  takenAt.value = new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Shanghai' }).replace(' ', 'T').slice(0, 16)
  await fetchRecords('/medication-records')
}

async function addMedication() {
  if (!newMed.value.name) return
  await createMed('/medications', {
    method: 'POST',
    body: JSON.stringify(newMed.value),
  })
  newMed.value = { name: '', category: '', default_dose: '' }
  showAddForm.value = false
  await fetchMeds('/medications')
}

async function removeMed(id: number) {
  if (!confirm('确定删除该药物？')) return
  await deleteMed(`/medications/${id}`, { method: 'DELETE' })
  await fetchMeds('/medications')
}

async function removeRecord(id: number) {
  if (!confirm('确定删除这条用药记录？')) return
  await deleteRecord(`/medication-records/${id}`, { method: 'DELETE' })
  await fetchRecords('/medication-records')
}

function openFeedback(rec: MedicationRecord) {
  editingRecordId.value = rec.id
  fbEffectiveness.value = rec.effectiveness
  fbSideEffects.value = rec.side_effects ? [...rec.side_effects] : []
  fbNote.value = rec.feedback_note ?? ''
  showFeedbackModal.value = true
}

async function saveFeedback() {
  if (!editingRecordId.value) return
  fbSaving.value = true
  await fetch(`/api/medication-records/${editingRecordId.value}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      effectiveness: fbEffectiveness.value,
      side_effects: fbSideEffects.value.length > 0 ? fbSideEffects.value : null,
      feedback_note: fbNote.value || null,
    }),
  })
  fbSaving.value = false
  showFeedbackModal.value = false
  await fetchRecords('/medication-records')
}

function toggleFbSideEffect(se: string) {
  const idx = fbSideEffects.value.indexOf(se)
  if (idx >= 0) fbSideEffects.value.splice(idx, 1)
  else fbSideEffects.value.push(se)
}

function formatTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const groupedRecords = computed(() => {
  if (!records.value) return {}
  const groups: Record<string, MedicationRecord[]> = {}
  for (const r of records.value) {
    const day = new Date(r.taken_at).toLocaleDateString('zh-CN')
    ;(groups[day] ??= []).push(r)
  }
  return groups
})

onMounted(load)
</script>

<template>
  <div class="max-w-4xl mx-auto py-6 sm:py-10 px-4 sm:px-6">
    <h2 class="font-marker text-2xl sm:text-4xl mb-8 rotate-[-1deg]">用药管理</h2>

    <!-- Quick Log -->
    <HandDrawnCard decoration="tack" class="mb-8">
      <h3 class="font-marker text-2xl mb-4">快速打卡</h3>
      <div class="flex flex-col gap-4">
        <!-- 药物选择 -->
        <div>
          <label class="font-marker text-lg text-[#2d2d2d] block mb-2">选择药物</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="med in medications"
              :key="med.id"
              type="button"
              class="px-4 py-2 border-2 border-[#2d2d2d] font-hand text-base transition-all duration-100 cursor-pointer"
              :class="selectedMedId === med.id
                ? 'bg-[#2d5da1] text-white shadow-[3px_3px_0px_0px_#2d2d2d]'
                : 'bg-white text-[#2d2d2d]'"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
              @click="selectMed(med)"
            >
              {{ med.name }}
            </button>
          </div>
        </div>

        <!-- 剂量 + 服药时间 -->
        <div class="flex flex-col sm:flex-row gap-4 items-end">
          <div class="flex-1">
            <HandDrawnInput v-model="dose" label="剂量" placeholder="例如：10mg" />
          </div>
          <div class="flex-1">
            <HandDrawnInput v-model="takenAt" label="服药时间" type="datetime-local" />
          </div>
          <label class="flex items-center gap-2 font-hand text-lg cursor-pointer pb-3 whitespace-nowrap">
            <input type="checkbox" v-model="isPrn" class="w-5 h-5 accent-[#ff4d4d]" />
            PRN（按需）
          </label>
        </div>

        <!-- Feedback toggle -->
        <button
          type="button"
          class="font-hand text-sm text-[#2d5da1] hover:underline text-left"
          @click="showFeedback = !showFeedback"
        >
          {{ showFeedback ? '收起用药反馈 ▲' : '添加用药反馈 ▼' }}
        </button>

        <!-- Feedback section -->
        <div v-if="showFeedback" class="border-2 border-[#2d2d2d]/20 p-4 space-y-4"
          :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
          <!-- Effectiveness rating -->
          <div>
            <label class="font-marker text-base text-[#2d2d2d] block mb-2">药效评价</label>
            <div class="flex gap-2">
              <button
                v-for="n in 5" :key="n"
                type="button"
                class="flex-1 py-3 border-2 border-[#2d2d2d] font-hand text-sm transition-all cursor-pointer"
                :class="effectiveness === n ? 'text-white shadow-[3px_3px_0px_0px_#2d2d2d]' : 'bg-white text-[#2d2d2d]/60'"
                :style="{
                  borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px',
                  backgroundColor: effectiveness === n ? effectivenessColors[n] : undefined
                }"
                @click="effectiveness = effectiveness === n ? null : n"
              >
                {{ effectivenessLabels[n] }}
              </button>
            </div>
          </div>

          <!-- Side effects -->
          <div>
            <label class="font-marker text-base text-[#2d2d2d] block mb-2">副作用（可多选）</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="se in sideEffectOptions" :key="se"
                type="button"
                class="px-3 py-1.5 border-2 font-hand text-sm transition-all cursor-pointer"
                :class="sideEffects.includes(se)
                  ? 'border-[#ff4d4d] bg-[#ff4d4d]/10 text-[#ff4d4d]'
                  : 'border-[#2d2d2d]/30 bg-white text-[#2d2d2d]/50'"
                :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
                @click="toggleSideEffect(se)"
              >
                {{ se }}
              </button>
            </div>
          </div>

          <!-- Feedback note -->
          <div>
            <label class="font-marker text-base text-[#2d2d2d] block mb-2">备注</label>
            <textarea
              v-model="feedbackNote"
              rows="2"
              placeholder="用药感受、特殊情况..."
              class="w-full border-2 border-[#2d2d2d] bg-white px-4 py-2.5 font-hand text-base"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
            />
          </div>
        </div>

        <HandDrawnButton
          :disabled="!selectedMedId || !dose || submitting"
          @click="quickLog"
        >
          {{ submitting ? '记录中...' : '一键记录' }}
        </HandDrawnButton>
      </div>
    </HandDrawnCard>

    <div class="grid md:grid-cols-2 gap-8">
      <!-- Medication List -->
      <div>
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
          <h3 class="font-marker text-2xl">我的药物</h3>
          <HandDrawnButton variant="secondary" class="text-sm px-3 py-1" @click="showAddForm = !showAddForm">
            {{ showAddForm ? '取消' : '+ 添加' }}
          </HandDrawnButton>
        </div>

        <!-- Add form -->
        <HandDrawnCard v-if="showAddForm" class="mb-4">
          <div class="flex flex-col gap-3">
            <HandDrawnInput v-model="newMed.name" label="药物名称" />
            <HandDrawnInput v-model="newMed.category" label="分类" placeholder="例如：抗组胺" />
            <HandDrawnInput v-model="newMed.default_dose" label="默认剂量" placeholder="例如：10mg" />
            <HandDrawnButton @click="addMedication">保存</HandDrawnButton>
          </div>
        </HandDrawnCard>

        <!-- Grouped list -->
        <div v-for="(meds, cat) in groupedMeds" :key="cat" class="mb-4">
          <p class="font-marker text-base text-[#2d2d2d]/60 mb-2">{{ cat }}</p>
          <div class="flex flex-col gap-2">
            <div
              v-for="med in meds"
              :key="med.id"
              class="flex items-center justify-between border-2 border-[#2d2d2d] bg-white px-4 py-2 font-hand"
              :style="{ borderRadius: '155px 15px 225px 15px / 15px 225px 15px 155px' }"
            >
              <div>
                <span class="text-lg">{{ med.name }}</span>
                <span v-if="med.default_dose" class="text-sm text-[#2d2d2d]/50 ml-2">{{ med.default_dose }}</span>
                <span v-if="med.is_system" class="text-xs text-[#2d5da1] ml-2">系统</span>
              </div>
              <button
                v-if="!med.is_system"
                class="text-[#ff4d4d] font-hand text-sm cursor-pointer hover:underline"
                @click="removeMed(med.id)"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Record History -->
      <div>
        <h3 class="font-marker text-2xl mb-4">用药历史</h3>
        <div v-if="!records?.length" class="font-hand text-lg text-[#2d2d2d]/40">
          暂无用药记录
        </div>
        <div v-for="(recs, day) in groupedRecords" :key="day" class="mb-4">
          <p class="font-marker text-base text-[#2d2d2d]/60 mb-2">{{ day }}</p>
          <div class="flex flex-col gap-2">
            <HandDrawnCard
              v-for="rec in recs"
              :key="rec.id"
              class="py-3 px-4"
            >
              <div class="flex items-center justify-between">
                <div>
                  <span class="font-hand text-lg font-bold">
                    {{ rec.medication?.name ?? `药物#${rec.medication_id}` }}
                  </span>
                  <span class="font-hand text-base text-[#2d2d2d]/70 ml-2">{{ rec.dose }}</span>
                  <span v-if="rec.is_prn" class="text-xs bg-[#e5e0d8] px-2 py-0.5 ml-2 font-hand">PRN</span>
                </div>
                <div class="flex items-center gap-3">
                  <span class="font-hand text-sm text-[#2d2d2d]/40">
                    {{ formatTime(rec.taken_at) }}
                  </span>
                  <button
                    class="text-[#2d5da1] font-hand text-sm cursor-pointer hover:underline"
                    @click="openFeedback(rec)"
                  >
                    {{ rec.effectiveness != null ? '查看反馈' : '反馈' }}
                  </button>
                  <button
                    class="text-[#ff4d4d] font-hand text-sm cursor-pointer hover:underline"
                    @click="removeRecord(rec.id)"
                  >
                    删除
                  </button>
                </div>
              </div>
              <!-- Inline feedback preview -->
              <div v-if="rec.effectiveness != null || (rec.side_effects && rec.side_effects.length > 0) || rec.feedback_note"
                class="mt-2 pt-2 border-t border-[#2d2d2d]/10 flex flex-wrap items-center gap-2">
                <span v-if="rec.effectiveness != null"
                  class="inline-flex items-center gap-1 px-2 py-0.5 font-hand text-xs border-2"
                  :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px', borderColor: effectivenessColors[rec.effectiveness], color: effectivenessColors[rec.effectiveness] }">
                  {{ effectivenessLabels[rec.effectiveness] }}
                </span>
                <span v-for="se in rec.side_effects" :key="se"
                  class="px-2 py-0.5 font-hand text-xs border-2 border-[#ff4d4d]/40 text-[#ff4d4d]/70"
                  :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
                  {{ se }}
                </span>
                <span v-if="rec.feedback_note" class="font-hand text-xs text-[#2d2d2d]/40 italic">
                  "{{ rec.feedback_note }}"
                </span>
              </div>
            </HandDrawnCard>
          </div>
        </div>
      </div>
    </div>

    <!-- Feedback Modal -->
    <div v-if="showFeedbackModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showFeedbackModal = false">
      <HandDrawnCard class="w-full max-w-md mx-4" decoration="tape">
        <h3 class="font-marker text-xl mb-5">用药反馈</h3>
        <div class="space-y-4">
          <div>
            <label class="font-marker text-base text-[#2d2d2d] block mb-2">药效评价</label>
            <div class="flex gap-2">
              <button
                v-for="n in 5" :key="n"
                type="button"
                class="flex-1 py-3 border-2 border-[#2d2d2d] font-hand text-sm transition-all cursor-pointer"
                :class="fbEffectiveness === n ? 'text-white shadow-[3px_3px_0px_0px_#2d2d2d]' : 'bg-white text-[#2d2d2d]/60'"
                :style="{
                  borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px',
                  backgroundColor: fbEffectiveness === n ? effectivenessColors[n] : undefined
                }"
                @click="fbEffectiveness = fbEffectiveness === n ? null : n"
              >
                {{ effectivenessLabels[n] }}
              </button>
            </div>
          </div>
          <div>
            <label class="font-marker text-base text-[#2d2d2d] block mb-2">副作用（可多选）</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="se in sideEffectOptions" :key="se"
                type="button"
                class="px-3 py-1.5 border-2 font-hand text-sm transition-all cursor-pointer"
                :class="fbSideEffects.includes(se)
                  ? 'border-[#ff4d4d] bg-[#ff4d4d]/10 text-[#ff4d4d]'
                  : 'border-[#2d2d2d]/30 bg-white text-[#2d2d2d]/50'"
                :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
                @click="toggleFbSideEffect(se)"
              >
                {{ se }}
              </button>
            </div>
          </div>
          <div>
            <label class="font-marker text-base text-[#2d2d2d] block mb-2">备注</label>
            <textarea
              v-model="fbNote"
              rows="3"
              placeholder="用药感受、特殊情况..."
              class="w-full border-2 border-[#2d2d2d] bg-white px-4 py-2.5 font-hand text-base"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
            />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <HandDrawnButton variant="secondary" @click="showFeedbackModal = false">取消</HandDrawnButton>
          <HandDrawnButton :disabled="fbSaving" @click="saveFeedback">{{ fbSaving ? '保存中...' : '保存' }}</HandDrawnButton>
        </div>
      </HandDrawnCard>
    </div>
  </div>
</template>
