<script setup lang="ts">
import { ref, watch } from 'vue'
import { useImageAnalysisStore } from '../stores/imageAnalysisStore'

const store = useImageAnalysisStore()
const photoRef = ref<HTMLImageElement | null>(null)

// Wenn sich das Bild im Store ändert, aktualisiere das angezeigte Bild
watch(() => store.currentImageData, (newImageData) => {
  if (photoRef.value && newImageData) {
    photoRef.value.src = newImageData;
  }
})

defineExpose({
  photoRef
})
</script>

<template>
  <div class="camera-output">
    <img ref="photoRef" alt="Das aufgenommene Foto erscheint hier." />
    <p v-if="store.uploadStatus" class="upload-status" :class="{
      'success': store.uploadStatus.includes('erfolgreich'),
      'error': store.uploadStatus.includes('Fehler'),
      'info': store.uploadStatus.includes('Analysiere') || store.uploadStatus.includes('hochgeladen')
    }">
      {{ store.uploadStatus }}
    </p>
    <div v-if="store.isUploading || store.isAnalyzing" class="spinner-container">
      <div class="spinner"></div>
    </div>
    <div v-if="store.analysisResult" class="analysis-result">
      <h3>Analyse-Ergebnis:</h3>
      <p>{{ store.analysisResult }}</p>
    </div>
  </div>
</template>

<style scoped>
.camera-output {
  margin-top: 1rem;
  width: 100%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.analysis-result {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  width: 100%;
  border-left: 4px solid #4DBA87;
}

.camera-output img {
  width: 100%;
  height: auto;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.upload-status {
  margin-top: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  width: 100%;
  text-align: center;
}

.success {
  background-color: #d4edda;
  color: #155724;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
}

.info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.spinner-container {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #4DBA87;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
