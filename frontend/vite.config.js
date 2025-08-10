import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      // 'lead-manager-6.preview.emergentagent.com',
      'eab94d3d-6f7f-4abd-b1bf-e8d0351be7a9.preview.emergentagent.com'
      // "*"
    ]
  },
})