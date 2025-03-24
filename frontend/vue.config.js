const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  // Proxy API requests während der Entwicklung
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  // Ausgabeverzeichnis für den Build
  outputDir: '../dist/frontend'
})
