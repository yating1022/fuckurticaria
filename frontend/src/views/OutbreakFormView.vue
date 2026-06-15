<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi } from '../composables/useApi'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'
import HandDrawnInput from '../components/ui/HandDrawnInput.vue'
import SeveritySlider from '../components/ui/SeveritySlider.vue'
import type { Outbreak, OutbreakCreate } from '../types/outbreak'

const router = useRouter()
const route = useRoute()
const { request, loading } = useApi<Outbreak>()

const isEdit = computed(() => !!route.params.id)

const form = ref<OutbreakCreate>({
  started_at: new Date().toISOString().slice(0, 16),
  ended_at: null,
  severity: 3,
  location_text: '',
  notes: '',
  trigger_guess: '',
})

const triggerGuess = computed({
  get: () => form.value.trigger_guess ?? '',
  set: (v: string) => { form.value.trigger_guess = v },
})
const notes = computed({
  get: () => form.value.notes ?? '',
  set: (v: string) => { form.value.notes = v },
})

const bodyParts = ['头部', '面部', '颈部', '手臂', '手部', '躯干', '背部', '腿部', '脚部', '全身']
const selectedParts = ref<string[]>([])

function togglePart(part: string) {
  const idx = selectedParts.value.indexOf(part)
  if (idx >= 0) {
    selectedParts.value.splice(idx, 1)
  } else {
    selectedParts.value.push(part)
  }
  form.value.location_text = selectedParts.value.join('、')
}

onMounted(async () => {
  if (isEdit.value) {
    const data = await request(`/outbreaks/${route.params.id}`)
    if (data) {
      form.value = {
        started_at: data.started_at?.slice(0, 16) ?? '',
        ended_at: data.ended_at?.slice(0, 16) ?? null,
        severity: data.severity,
        location_text: data.location_text ?? '',
        notes: data.notes ?? '',
        trigger_guess: data.trigger_guess ?? '',
      }
      selectedParts.value = (data.location_text ?? '').split('、').filter(Boolean)
    }
  }
})

async function submit() {
  const method = isEdit.value ? 'PUT' : 'POST'
  const url = isEdit.value ? `/outbreaks/${route.params.id}` : '/outbreaks'
  const result = await request(url, {
    method,
    body: JSON.stringify(form.value),
  })
  if (result) {
    router.push('/outbreaks')
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto py-6 sm:py-10 px-4 sm:px-6">
    <h2 class="font-marker text-2xl sm:text-4xl mb-8 rotate-[-1deg]">
      {{ isEdit ? '编辑发病记录' : '记录发病' }}
    </h2>

    <HandDrawnCard decoration="tack">
      <form @submit.prevent="submit" class="flex flex-col gap-6">
        <!-- 时间 -->
        <HandDrawnInput
          v-model="form.started_at"
          label="发病时间"
          type="datetime-local"
        />

        <!-- 严重程度 -->
        <SeveritySlider v-model="form.severity!" />

        <!-- 部位选择 -->
        <div class="flex flex-col gap-2">
          <label class="font-marker text-lg text-[#2d2d2d]">发病部位</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="part in bodyParts"
              :key="part"
              type="button"
              class="px-4 py-2 border-2 border-[#2d2d2d] font-hand text-base transition-all duration-100 cursor-pointer"
              :class="selectedParts.includes(part)
                ? 'bg-[#ff4d4d] text-white shadow-[3px_3px_0px_0px_#2d2d2d]'
                : 'bg-white text-[#2d2d2d]'"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
              @click="togglePart(part)"
            >
              {{ part }}
            </button>
          </div>
        </div>

        <!-- 触发源 -->
        <HandDrawnInput
          v-model="triggerGuess"
          label="猜测触发源"
          placeholder="例如：压力、海鲜、天气变化..."
        />

        <!-- 备注 -->
        <HandDrawnInput
          v-model="notes"
          label="备注"
          type="textarea"
          placeholder="补充说明..."
        />

        <!-- 操作按钮 -->
        <div class="flex gap-4 justify-end mt-4">
          <HandDrawnButton variant="secondary" @click="router.back()">
            取消
          </HandDrawnButton>
          <HandDrawnButton type="submit" :disabled="loading">
            {{ loading ? '保存中...' : (isEdit ? '更新' : '记录') }}
          </HandDrawnButton>
        </div>
      </form>
    </HandDrawnCard>
  </div>
</template>
