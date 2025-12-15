import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  base: "/",
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        // 🔥 MODO DEV:
        // Usa el puerto 5000 si ejecutas `python app.py` manualmente.
        // Usa localhost si estás con Nginx reverse proxy en Docker.
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})