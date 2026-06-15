<script setup lang="ts">
import { useRouter } from 'vue-router'
import HandDrawnButton from '../components/ui/HandDrawnButton.vue'
import HandDrawnCard from '../components/ui/HandDrawnCard.vue'

const router = useRouter()
</script>

<template>
  <div class="max-w-3xl mx-auto py-16 px-6">
    <div class="text-center mb-12">
      <h1 class="font-marker text-5xl md:text-6xl mb-4 rotate-[-1deg]">
        FuckUrticaria
      </h1>
      <p class="font-hand text-xl text-[#2d2d2d]/70">
        去他妈的荨麻疹 — 记录、分析、掌控
      </p>
    </div>

    <div class="grid md:grid-cols-2 gap-6">
      <HandDrawnCard decoration="tape" class="hover:rotate-[-1deg] transition-transform duration-200">
        <h3 class="font-marker text-2xl mb-3">发病记录</h3>
        <p class="font-hand text-lg text-[#2d2d2d]/70 mb-4">
          快速记录每次发病的时间、部位和严重程度
        </p>
        <HandDrawnButton @click="router.push('/outbreaks')">
          查看记录
        </HandDrawnButton>
      </HandDrawnCard>

      <HandDrawnCard decoration="tack" class="hover:rotate-[1deg] transition-transform duration-200">
        <h3 class="font-marker text-2xl mb-3">用药管理</h3>
        <p class="font-hand text-lg text-[#2d2d2d]/70 mb-4">
          追踪用药信息，记录剂量和时间
        </p>
        <HandDrawnButton variant="secondary" @click="router.push('/medications')">
          用药管理
        </HandDrawnButton>
      </HandDrawnCard>

      <HandDrawnCard decoration="tape" class="hover:rotate-[-0.5deg] transition-transform duration-200">
        <h3 class="font-marker text-2xl mb-3">AI 分析</h3>
        <p class="font-hand text-lg text-[#2d2d2d]/70 mb-4">
          基于大模型的智能健康分析报告
        </p>
        <HandDrawnButton variant="secondary" @click="router.push('/ai')">
          查看分析
        </HandDrawnButton>
      </HandDrawnCard>
    </div>
  </div>
</template>
