import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'
import {visualizer} from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig(({mode}) => {
    const isAnalyze = mode === 'analyze';

    return {
        plugins: [
            react(),
            isAnalyze && visualizer({
                open: false, // Don't open in browser automatically (better for CI)
                filename: 'dist-analyze/stats.html',
                gzipSize: true,
                brotliSize: true,
            }),
        ].filter(Boolean),
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
    };
});
