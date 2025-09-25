import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import VueDevTools from 'vite-plugin-vue-devtools'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    VueDevTools()
  ],
  resolve: {
    alias: {
      '@': resolve('./src')
    }
  },
  server: {
    port: 8000,
    strictPort: true, // Fail if port 8000 is not available, don't try other ports
    proxy: {
      '/calendars': {
        target: process.env.NODE_ENV === 'development' && process.env.DOCKER_ENV 
          ? 'http://backend-dev:3000'  // Docker container communication
          : 'http://localhost:3000',   // Native development
        changeOrigin: true
      },
      '/domains': {
        target: process.env.NODE_ENV === 'development' && process.env.DOCKER_ENV 
          ? 'http://backend-dev:3000'  // Docker container communication
          : 'http://localhost:3000',   // Native development
        changeOrigin: true
      },
      '/ical': {
        target: process.env.NODE_ENV === 'development' && process.env.DOCKER_ENV 
          ? 'http://backend-dev:3000'  // Docker container communication
          : 'http://localhost:3000',   // Native development
        changeOrigin: true
      },
      '/test': {
        target: process.env.NODE_ENV === 'development' && process.env.DOCKER_ENV 
          ? 'http://backend-dev:3000'  // Docker container communication
          : 'http://localhost:3000',   // Native development
        changeOrigin: true
      },
      '/health': {
        target: process.env.NODE_ENV === 'development' && process.env.DOCKER_ENV
          ? 'http://backend-dev:3000'  // Docker container communication  
          : 'http://localhost:3000',   // Native development
        changeOrigin: true
      }
    }
  }
})