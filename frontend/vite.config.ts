import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'

// GitHub Pages has no SPA fallback and serves 404.html for any path without a
// matching file. Shipping a copy of index.html as 404.html lets the router
// handle direct visits to client-side routes like /log.
function spaFallback(): Plugin {
  return {
    name: 'spa-fallback-404',
    apply: 'build',
    enforce: 'post',
    generateBundle(_options, bundle) {
      const index = bundle['index.html']
      if (!index || index.type !== 'asset') {
        this.error('index.html was not found in the bundle')
      }
      this.emitFile({ type: 'asset', fileName: '404.html', source: index.source })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tanstackRouter({ target: 'react', autoCodeSplitting: true }),
    react(),
    tailwindcss(),
    spaFallback(),
  ],
})
