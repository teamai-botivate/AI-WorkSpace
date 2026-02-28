import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5175,
    // Allow embedding inside Botivate workspace shell (iframe on port 3000)
    headers: {
      'X-Frame-Options': 'ALLOWALL',
    },
    cors: true,
  },
})
