import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

const configPath = path.resolve(__dirname, '../config.json')
let appConfig = { backend_port: 8000, frontend_port: 5173, p2p_port: 47833 }
if (fs.existsSync(configPath)) {
  try {
    appConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'))
  } catch (e) {
    console.warn('Failed to read config.json, using defaults')
  }
}

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  server: {
    port: appConfig.frontend_port || 5173,
    proxy: mode === 'tauri'
      ? undefined
      : {
          '/api': {
            target: `http://localhost:${appConfig.backend_port || 8000}`,
            changeOrigin: true
          }
        }
  }
}))
