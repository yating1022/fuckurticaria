<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const menuOpen = ref(false)

const links = [
  { name: '首页', path: '/' },
  { name: '发病记录', path: '/outbreaks' },
  { name: '趋势图表', path: '/charts' },
  { name: '用药管理', path: '/medications' },
  { name: 'UAS7评分', path: '/uas7' },
  { name: '生活打卡', path: '/lifestyle' },
  { name: '环境数据', path: '/weather' },
  { name: 'AI分析', path: '/ai' },
  { name: '设置', path: '/admin' },
]

function navigate(path: string) {
  menuOpen.value = false
  router.push(path)
}
</script>

<template>
  <nav class="border-b-2 border-[#2d2d2d] bg-[#fdfbf7] px-4 sm:px-6 py-3 sm:py-4">
    <div class="max-w-5xl mx-auto flex items-center justify-between">
      <h1
        class="font-marker text-xl sm:text-2xl text-[#2d2d2d] cursor-pointer rotate-[-1deg]"
        @click="navigate('/')"
      >
        FuckUrticaria
      </h1>

      <!-- Desktop nav -->
      <div class="hidden md:flex gap-6">
        <router-link
          v-for="link in links"
          :key="link.path"
          :to="link.path"
          class="font-hand text-lg text-[#2d2d2d] relative
                 after:absolute after:bottom-[-2px] after:left-0 after:w-full after:h-[2px]
                 after:bg-[#2d2d2d] after:scale-x-0 after:transition-transform after:duration-200
                 hover:after:scale-x-100"
          :class="{ 'font-bold after:scale-x-100': route.path === link.path }"
        >
          {{ link.name }}
        </router-link>
      </div>

      <!-- Mobile hamburger -->
      <button
        type="button"
        class="md:hidden w-10 h-10 flex flex-col items-center justify-center gap-1.5 cursor-pointer"
        @click="menuOpen = !menuOpen"
        aria-label="菜单"
      >
        <span class="w-6 h-0.5 bg-[#2d2d2d] transition-transform duration-200"
              :class="menuOpen ? 'rotate-45 translate-y-[4px]' : ''"></span>
        <span class="w-6 h-0.5 bg-[#2d2d2d] transition-opacity duration-200"
              :class="menuOpen ? 'opacity-0' : ''"></span>
        <span class="w-6 h-0.5 bg-[#2d2d2d] transition-transform duration-200"
              :class="menuOpen ? '-rotate-45 -translate-y-[4px]' : ''"></span>
      </button>
    </div>
  </nav>

  <!-- Mobile drawer overlay -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="menuOpen"
        class="fixed inset-0 bg-black/30 z-40 md:hidden"
        @click="menuOpen = false"
      />
    </Transition>
    <Transition name="slide">
      <div
        v-if="menuOpen"
        class="fixed top-0 right-0 h-full w-64 bg-[#fdfbf7] border-l-2 border-[#2d2d2d] z-50 md:hidden overflow-y-auto"
      >
        <div class="p-6 pt-4">
          <p class="font-marker text-lg text-[#2d2d2d]/40 mb-6 rotate-[-1deg]">导航</p>
          <div class="flex flex-col gap-1">
            <button
              v-for="link in links"
              :key="link.path"
              type="button"
              class="text-left font-hand text-lg px-4 py-3 border-2 cursor-pointer transition-all duration-100"
              :class="route.path === link.path
                ? 'border-[#2d2d2d] bg-[#2d5da1] text-white shadow-[3px_3px_0px_0px_#2d2d2d]'
                : 'border-transparent text-[#2d2d2d]'"
              :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
              @click="navigate(link.path)"
            >
              {{ link.name }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.slide-enter-active, .slide-leave-active {
  transition: transform 0.25s ease;
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(100%);
}
</style>
