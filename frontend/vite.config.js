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
      '30ac7fac-5c43-4846-ac99-edfa626ede7e.preview.emergentagent.com',
      "business-suite-6.preview.emergentagent.com"
    ]
  },
})