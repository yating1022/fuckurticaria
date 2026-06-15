<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
  type?: 'button' | 'submit'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  disabled: false,
  type: 'button',
})

const variantClasses: Record<string, string> = {
  primary:
    'bg-white border-[#2d2d2d] text-[#2d2d2d] hover:bg-[#ff4d4d] hover:text-white',
  secondary:
    'bg-[#e5e0d8] border-[#2d2d2d] text-[#2d2d2d] hover:bg-[#2d5da1] hover:text-white',
  danger:
    'bg-white border-[#ff4d4d] text-[#ff4d4d] hover:bg-[#ff4d4d] hover:text-white',
}
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    class="border-[3px] px-6 py-3 font-hand text-lg shadow-[4px_4px_0px_0px_#2d2d2d]
           transition-all duration-100 cursor-pointer
           hover:shadow-[2px_2px_0px_0px_#2d2d2d] hover:translate-x-[2px] hover:translate-y-[2px]
           active:shadow-none active:translate-x-[4px] active:translate-y-[4px]
           disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-x-0 disabled:translate-y-0"
    :class="variantClasses[variant]"
    :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }"
  >
    <slot />
  </button>
</template>
