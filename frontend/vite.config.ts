import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    port: 2563,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5241',
        changeOrigin: true,
      },
    },
  },
})
