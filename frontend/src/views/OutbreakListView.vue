<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'
import type { Outbreak } from '../types/outbreak'

const router = useRouter()
const { data: outbreaks, loading, error, request } = useApi<Outbreak[]>()
const { request: deleteReq } = useApi<{ detail: string }>()

const severityLabels: Record<number, { text: string; color: string }> = {
  1: { text: '轻微', color: '#4ade80' },
  2: { text: '较轻', color: '#facc15' },
  3: { text: '中度', color: '#fb923c' },
  4: { text: '较重', color: '#f87171' },
  5: { text: '严重', color: '#dc2626' },
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' })
    + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function load() {
  await request('/outbreaks')
}

async function remove(id: number) {
  if (!confirm('确定删除这条记录？')) return
  await deleteReq(`/outbreaks/${id}`, { method: 'DELETE' })
  await load()
}

onMounted(load)
</script>

<template>
  <div class="max-w-3xl mx-auto py-10 px-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-8">
      <h2 class="font-marker text-2xl sm:text-4xl rotate-[-1deg]">发病记录</h2>
      <HandDrawnButton @click="router.push('/outbreaks/new')">
        + 记录发病
      </HandDrawnButton>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="font-hand text-xl text-[#2d2d2d]/60 text-center py-20">
      加载中...
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="font-hand text-xl text-[#ff4d4d] text-center py-20">
      {{ error }}
    </div>

    <!-- 空状态 -->
    <div v-else-if="!outbreaks?.length" class="text-center py-20">
      <HandDrawnCard>
        <p class="font-hand text-xl text-[#2d2d2d]/60 mb-4">
          还没有发病记录，点击上方按钮开始记录
        </p>
      </HandDrawnCard>
    </div>

    <!-- 记录列表 -->
    <div v-else class="flex flex-col gap-4">
      <HandDrawnCard
        v-for="item in outbreaks"
        :key="item.id"
        class="hover:rotate-[-0.5deg] transition-transform duration-200 cursor-pointer"
        @click="router.push(`/outbreaks/${item.id}/edit`)"
      >
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div class="flex-1 min-w-0">
            <!-- 时间 & 严重程度 -->
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span class="font-marker text-base sm:text-lg">{{ formatDate(item.started_at) }}</span>
              <span
                v-if="item.severity"
                class="px-3 py-0.5 border-2 border-[#2d2d2d] font-hand text-sm"
                :style="{
                  borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px',
                  backgroundColor: severityLabels[item.severity]?.color,
                }"
              >
                {{ severityLabels[item.severity]?.text }}
              </span>
            </div>

            <!-- 部位 -->
            <p v-if="item.location_text" class="font-hand text-base text-[#2d2d2d] mb-1">
              部位：{{ item.location_text }}
            </p>

            <!-- 触发源 -->
            <p v-if="item.trigger_guess" class="font-hand text-base text-[#2d2d2d]/60">
              可能触发源：{{ item.trigger_guess }}
            </p>

            <!-- 备注 -->
            <p v-if="item.notes" class="font-hand text-sm text-[#2d2d2d]/40 mt-1 truncate">
              {{ item.notes }}
            </p>
          </div>

          <!-- 删除按钮 -->
          <HandDrawnButton
            variant="danger"
            class="shrink-0 text-sm px-3 py-1 self-end sm:self-auto"
            @click.stop="remove(item.id)"
          >
            删除
          </HandDrawnButton>
        </div>
      </HandDrawnCard>
    </div>
  </div>
</template>
