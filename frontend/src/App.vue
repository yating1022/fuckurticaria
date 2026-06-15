<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/layout/Navbar.vue'

const route = useRoute()
const showNavbar = computed(() => route.name !== 'login')
</script>

<template>
  <div class="min-h-screen bg-[#fdfbf7]">
    <Navbar v-if="showNavbar" />
    <router-view />
  </div>
</template>
