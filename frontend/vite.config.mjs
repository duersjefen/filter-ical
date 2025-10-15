import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import VueDevTools from 'vite-plugin-vue-devtools'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    // Only include VueDevTools in development mode
    ...(process.env.NODE_ENV !== 'production' ? [VueDevTools()] : [])
  ],
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // Remove all console.* calls in production
        drop_debugger: true,   // Remove debugger statements
        pure_funcs: ['console.log', 'console.info', 'console.debug']  // Explicitly mark as pure for aggressive removal
      }
    },
    // Increase chunk size warning limit (we're code-splitting intentionally)
    chunkSizeWarningLimit: 600,
    cssCodeSplit: true,  // Split CSS into separate files per chunk
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks for better caching
          'vue-core': ['vue', 'vue-router'],
          'vue-libs': ['pinia', 'vue-i18n'],
          'http': ['axios']
        },
        // Optimize asset naming for better caching
        assetFileNames: (assetInfo) => {
          // CSS files get their own naming pattern
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'assets/css/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve('./src')
    }
  },
  server: {
    port: 8000,
    strictPort: true, // Fail if port 8000 is not available, don't try other ports
    proxy: {
      '/api': {
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
      '/test/': {
        // Note: trailing slash ensures /test3 (domain) doesn't match /test/ (endpoint)
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