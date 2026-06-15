<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'

interface SettingOut {
  key: string
  value: string | null
  description: string | null
}

const { data, loading, request: fetchSettings } = useApi<SettingOut[]>()
const settings = computed(() => data.value ?? [])
const saveStates = ref<Record<string, boolean>>({})
const editValues = ref<Record<string, string>>({})
const saveMsg = ref<Record<string, string>>({})
const showKey = ref<Record<string, boolean>>({})

async function load() {
  await fetchSettings('/admin/settings')
  if (settings.value) {
    for (const s of settings.value) {
      editValues.value[s.key] = s.value ?? ''
    }
  }
}

async function saveSetting(key: string) {
  saveStates.value[key] = true
  saveMsg.value[key] = ''
  try {
    const res = await fetch(`/api/admin/settings/${key}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: editValues.value[key] }),
    })
    if (!res.ok) throw new Error(await res.text())
    saveMsg.value[key] = '已保存 ✓'
    setTimeout(() => { saveMsg.value[key] = '' }, 2000)
  } catch (e: any) {
    saveMsg.value[key] = '保存失败: ' + (e?.message || '未知错误')
  } finally {
    saveStates.value[key] = false
  }
}

function isSecret(key: string) {
  return key.includes('key') || key.includes('secret') || key.includes('password')
}

onMounted(load)
</script>

<template>
  <div class="max-w-3xl mx-auto py-6 sm:py-10 px-4 sm:px-6">
    <div class="mb-8">
      <h2 class="font-marker text-2xl sm:text-4xl rotate-[-1deg]">管理后台</h2>
      <p class="font-hand text-base text-[#2d2d2d]/50 mt-1">配置 AI 分析等系统设置</p>
    </div>

    <div v-if="loading" class="font-hand text-xl text-[#2d2d2d]/40 text-center py-20">加载中...</div>

    <template v-else>
      <HandDrawnCard decoration="tape" class="mb-6">
        <h3 class="font-marker text-xl mb-5">DeepSeek AI 设置</h3>
        <div
          v-for="s in settings?.filter(s => s.key.startsWith('deepseek'))"
          :key="s.key"
          class="mb-5 last:mb-0"
        >
          <label class="block font-hand text-sm text-[#2d2d2d]/50 mb-1">
            {{ s.description ?? s.key }}
          </label>
          <div class="flex items-center gap-3">
            <div class="flex-1 relative">
              <input
                v-model="editValues[s.key]"
                :type="isSecret(s.key) && !showKey[s.key] ? 'password' : 'text'"
                class="w-full border-2 border-[#2d2d2d] bg-white px-4 py-2.5 font-hand text-base pr-10"
                :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
                :placeholder="s.description ?? ''"
              />
              <button
                v-if="isSecret(s.key)"
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 font-hand text-xs text-[#2d2d2d]/40 hover:text-[#2d2d2d]/70"
                @click="showKey[s.key] = !showKey[s.key]"
              >
                {{ showKey[s.key] ? '隐藏' : '显示' }}
              </button>
            </div>
            <HandDrawnButton
              variant="secondary"
              :disabled="saveStates[s.key]"
              @click="saveSetting(s.key)"
            >
              {{ saveStates[s.key] ? '保存中...' : '保存' }}
            </HandDrawnButton>
            <span
              v-if="saveMsg[s.key]"
              class="font-hand text-sm whitespace-nowrap"
              :class="saveMsg[s.key].includes('失败') ? 'text-[#ff4d4d]' : 'text-[#4ade80]'"
            >
              {{ saveMsg[s.key] }}
            </span>
          </div>
        </div>
      </HandDrawnCard>

      <HandDrawnCard class="mb-6">
        <h3 class="font-marker text-xl mb-3">使用说明</h3>
        <ul class="space-y-2 font-hand text-base text-[#2d2d2d]/70 leading-relaxed">
          <li>• 前往 <span class="text-[#2d5da1]">platform.deepseek.com</span> 获取 API Key</li>
          <li>• API Key 会保存在本地数据库中，不会上传到任何第三方服务</li>
          <li>• AI 分析会发送你近 N 天的健康数据到 DeepSeek 进行分析</li>
          <li>• 分析结果仅供参考，不构成医学建议，请遵医嘱</li>
        </ul>
      </HandDrawnCard>

      <div class="flex justify-end mt-6">
        <div class="border-2 border-[#2d2d2d] bg-white px-4 py-2 font-hand text-sm text-[#2d2d2d]/40"
             :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">
          设置项总数: {{ settings?.length ?? 0 }}
        </div>
      </div>
    </template>
  </div>
</template>
