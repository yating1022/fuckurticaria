<script setup lang="ts">
interface Props {
  decoration?: 'tape' | 'tack' | 'none'
}

const props = withDefaults(defineProps<Props>(), {
  decoration: 'none',
})
</script>

<template>
  <div class="relative border-2 border-[#2d2d2d] bg-white p-6 shadow-[3px_3px_0px_0px_rgba(45,45,45,0.1)]"
       :style="{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }">

    <!-- Tape decoration -->
    <div v-if="decoration === 'tape'"
         class="absolute -top-3 left-1/2 -translate-x-1/2 w-20 h-6 bg-[#e5e0d8]/70 rotate-[-2deg] rounded-sm" />

    <!-- Tack decoration -->
    <div v-if="decoration === 'tack'"
         class="absolute -top-3 left-1/2 -translate-x-1/2 w-6 h-6 bg-[#ff4d4d] rounded-full border-2 border-[#2d2d2d]" />

    <slot />
  </div>
</template>
