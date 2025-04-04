<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useImageAnalysisStore } from './stores/imageAnalysisStore'

// Store initialisieren
const store = useImageAnalysisStore()
</script>

<template>
  <RouterView />
</template>

<style>
/* Globale Stile */
body {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0;
  padding: 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}
</style>
