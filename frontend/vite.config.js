import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { sentryVitePlugin } from '@sentry/vite-plugin'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(() => {
  const sentryEnabled = Boolean(
    process.env.SENTRY_AUTH_TOKEN &&
      process.env.SENTRY_ORG &&
      process.env.SENTRY_PROJECT
  )

  return {
    plugins: [
      react(),
      tailwindcss(),
      sentryEnabled
        ? sentryVitePlugin({
            org: process.env.SENTRY_ORG,
            project: process.env.SENTRY_PROJECT,
            authToken: process.env.SENTRY_AUTH_TOKEN,
            release: process.env.SENTRY_RELEASE || process.env.GITHUB_SHA,
            telemetry: false,
          })
        : null,
    ].filter(Boolean),
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      // Optimize for better tree-shaking
      rollupOptions: {
        output: {
          manualChunks: {
            'lucide-react': ['lucide-react'],
          },
        },
      },
      // Target modern browsers
      target: 'es2020',
      // Enable source maps for debugging
      sourcemap: true,
      // Optimize chunks
      chunkSizeWarningLimit: 600,
    },
    optimizeDeps: {
      // Pre-bundle lucide-react for faster dev starts
      include: ['lucide-react'],
      // Force re-optimization of lucide-react
      force: true,
    },
    define: {
      // Define global constants
      __DEV__: JSON.stringify(process.env.NODE_ENV !== 'production'),
    },
  }
})
