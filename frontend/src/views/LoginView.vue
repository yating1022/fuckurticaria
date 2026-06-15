<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'
import HandDrawnInput from '../components/ui/HandDrawnInput.vue'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import { useApi } from '../composables/useApi'

const router = useRouter()
const { loading, error, request } = useApi<{ access_token: string }>()

const password = ref('')
const shake = ref(false)

async function handleLogin() {
  if (!password.value.trim()) {
    shake.value = true
    setTimeout(() => (shake.value = false), 500)
    return
  }

  const res = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ password: password.value }),
  })

  if (res?.access_token) {
    localStorage.setItem('token', res.access_token)
    router.push('/')
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#fdfbf7] flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <HandDrawnCard>
        <div class="flex flex-col items-center gap-6 p-4">
          <!-- Logo / Title -->
          <div class="text-center">
            <h1 class="font-marker text-3xl sm:text-4xl text-[#2d2d2d] rotate-[-1deg]">
              FuckUrticaria
            </h1>
            <p class="font-hand text-lg text-[#2d2d2d]/60 mt-1">
              去他妈的荨麻疹
            </p>
          </div>

          <!-- Divider -->
          <div
            class="w-full border-t-2 border-dashed border-[#2d2d2d]/20"
            style="border-radius: 0"
          />

          <!-- Form -->
          <div
            class="w-full flex flex-col gap-4"
            :class="{ animate: shake }"
            style="--shake-distance: 8px"
          >
            <HandDrawnInput
              v-model="password"
              label="访问密码"
              type="password"
              placeholder="请输入访问密码"
              @keyup.enter="handleLogin"
            />

            <p v-if="error" class="font-hand text-[#ff4d4d] text-base">
              {{ error }}
            </p>

            <HandDrawnButton
              class="w-full mt-2"
              :disabled="loading"
              @click="handleLogin"
            >
              {{ loading ? '验证中...' : '进入系统' }}
            </HandDrawnButton>
          </div>

          <!-- Footer hint -->
          <p class="font-hand text-sm text-[#2d2d2d]/40 text-center">
            记录 · 分析 · 战胜荨麻疹
          </p>
        </div>
      </HandDrawnCard>
    </div>
  </div>
</template>

<style scoped>
.animate {
  animation: shake 0.4s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(calc(-1 * var(--shake-distance, 8px))); }
  40% { transform: translateX(var(--shake-distance, 8px)); }
  60% { transform: translateX(calc(-0.5 * var(--shake-distance, 8px))); }
  80% { transform: translateX(calc(0.5 * var(--shake-distance, 8px))); }
}
</style>
