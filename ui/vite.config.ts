import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            "^/zone": "http://localhost:8000",
            "^/state": "http://localhost:8000",
            "^/static": "http://localhost:8000",
            "^/command": "http://localhost:8000",
            "^/api": "http://localhost:8000"
        }
    },
    root: '.',
    build: {
        rollupOptions: {
            input: './index.html'
        }
    }
});
