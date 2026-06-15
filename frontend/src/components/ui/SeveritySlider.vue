<script setup lang="ts">
interface Props {
  modelValue: number
}

defineProps<Props>()
defineEmits<{ 'update:modelValue': [value: number] }>()

const levels = [
  { value: 1, label: '轻微', color: '#4ade80' },
  { value: 2, label: '较轻', color: '#facc15' },
  { value: 3, label: '中度', color: '#fb923c' },
  { value: 4, label: '较重', color: '#f87171' },
  { value: 5, label: '严重', color: '#dc2626' },
]
</script>

<template>
  <div class="flex flex-col gap-2">
    <label class="font-marker text-lg text-[#2d2d2d]">严重程度</label>
    <div class="grid grid-cols-3 sm:grid-cols-5 gap-2">
      <button
        v-for="level in levels"
        :key="level.value"
        type="button"
        class="py-3 border-2 border-[#2d2d2d] font-hand text-base transition-all duration-100 cursor-pointer
               hover:shadow-[2px_2px_0px_0px_#2d2d2d]"
        :class="modelValue === level.value
          ? 'text-white shadow-[3px_3px_0px_0px_#2d2d2d]'
          : 'bg-white text-[#2d2d2d]'"
        :style="{
          borderRadius: '155px 15px 225px 15px / 15px 225px 15px 155px',
          backgroundColor: modelValue === level.value ? level.color : undefined,
        }"
        @click="$emit('update:modelValue', level.value)"
      >
        {{ level.label }}
      </button>
    </div>
  </div>
</template>
