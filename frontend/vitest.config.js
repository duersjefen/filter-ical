import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve('./src')
    }
  },
  test: {
    environment: 'jsdom',
    setupFiles: [
      './tests/setup.js',
      './tests/setup/consoleMonitor.js',
      './tests/setup/vueErrorHandler.js',
      './tests/setup/i18nErrorHandler.js'
    ],
    globals: true,
    testTimeout: 10000, // 10 second default timeout
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**',
      '**/tests/e2e/**', // Exclude E2E tests from Vitest
      '**/{playwright-report,test-results}/**',
      '**/*.e2e.test.js' // Skip E2E tests
    ]
  }
});