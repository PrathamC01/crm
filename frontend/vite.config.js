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
      'lead-manager-6.preview.emergentagent.com',
      '45ef8d04-cd5e-471a-9a5d-2989f488e28b.preview.emergentagent.com'
    ]
  },
})