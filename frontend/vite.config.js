import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Use VITE_BASE environment variable (set by CI) if provided,
// otherwise fall back to '/'. This allows GitHub Actions to set
// the correct base automatically for GitHub Pages deployments.
const base = process.env.VITE_BASE || '/'

// https://vite.dev/config/
export default defineConfig({
  base,
  plugins: [react()],
})
