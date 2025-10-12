import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/socket.io': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
    hmr: {
      overlay: true,
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV === 'development',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          // Core vendor chunks
          'vendor-react': ['react', 'react-dom'],
          'vendor-router': ['react-router-dom'],
          'vendor-redux': ['@reduxjs/toolkit', 'react-redux'],
          'vendor-mui': ['@mui/material', '@mui/icons-material', '@mui/lab'],
          'vendor-clerk': ['@clerk/clerk-react'],

          // Feature-specific chunks for better mobile loading
          'feature-mobile': [
            './src/components/mobile',
            './src/services/websocket',
            './src/services/haptics',
            './src/services/offlineSync',
            './src/services/pushNotifications'
          ],
          'feature-deals': ['./src/features/deals'],
          'feature-ai': ['./src/features/ai'],

          // Heavy libraries
          'vendor-swiper': ['swiper'],
          'vendor-idb': ['idb'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@mui/material',
      '@mui/icons-material',
      '@clerk/clerk-react',
      '@reduxjs/toolkit',
      'react-redux',
    ],
    exclude: [
      'swiper',
      'idb',
    ],
  },
  define: {
    __PWA_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
  worker: {
    format: 'es',
  },
  preview: {
    port: 4173,
    host: true,
  },
});