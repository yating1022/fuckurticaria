<script setup lang="ts">
interface Props {
  modelValue: string
  label?: string
  type?: 'text' | 'textarea' | 'datetime-local' | 'password'
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
})

defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="font-marker text-lg text-[#2d2d2d]">{{ label }}</label>
    <textarea
      v-if="type === 'textarea'"
      :value="modelValue"
      :placeholder="placeholder"
      rows="3"
      class="border-2 border-[#2d2d2d] bg-white px-4 py-3 font-hand text-lg
             placeholder:text-[#2d2d2d]/40
             focus:border-[#2d5da1] focus:ring-2 focus:ring-[#2d5da1]/20 focus:outline-none"
      :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
    <input
      v-else
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      class="border-2 border-[#2d2d2d] bg-white px-4 py-3 font-hand text-lg
             placeholder:text-[#2d2d2d]/40
             focus:border-[#2d5da1] focus:ring-2 focus:ring-[#2d5da1]/20 focus:outline-none"
      :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>
