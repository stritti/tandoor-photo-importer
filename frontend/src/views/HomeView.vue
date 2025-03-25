<script setup lang="ts">
import { ref, watch } from 'vue'
import CameraUpload from '@/components/CameraUpload.vue'

const uploadResult = ref<any>(null)
const aiResult = ref<any>(null)
const cameraUploadRef = ref<InstanceType<typeof CameraUpload> | null>(null)
const isLoading = ref(false)

function handlePhotoTaken(photoData: string) {
  console.log('Foto aufgenommen!')
  // Zurücksetzen der Ergebnisse bei neuem Foto
  uploadResult.value = null
  aiResult.value = null
}

function handlePhotoUploaded(result: any) {
  uploadResult.value = result
  console.log('Foto hochgeladen!', result)
  
  // Wenn KI-Analyse vorhanden ist, extrahieren
  if (result.ai_analysis) {
    aiResult.value = result.ai_analysis
    isLoading.value = false
  } else {
    isLoading.value = true
  }
}

async function analyzeImage() {
  if (!uploadResult.value || !uploadResult.value.path) {
    alert('Bitte zuerst ein Foto hochladen!')
    return
  }
  
  isLoading.value = true
  try {
    if (cameraUploadRef.value) {
      const result = await cameraUploadRef.value.analyzeExistingImage(uploadResult.value.path)
      aiResult.value = result.ai_analysis
    }
  } catch (error) {
    console.error('Fehler bei der Analyse:', error)
  } finally {
    isLoading.value = false
  }
}

// Wenn aiResult gesetzt wird, Loading-Status zurücksetzen
watch(aiResult, (newValue) => {
  if (newValue) {
    isLoading.value = false
  }
})
</script>

<template>
  <main>
    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">KI analysiert das Bild...</div>
    </div>
    
    <div class="app-container">
      <h1>Kamera App mit KI-Analyse</h1>

      <CameraUpload
        ref="cameraUploadRef"
        @photo-taken="handlePhotoTaken"
        @photo-uploaded="handlePhotoUploaded"
      />

      <div v-if="uploadResult" class="result-container">
        <div class="upload-result">
          <h3>Upload-Ergebnis:</h3>
          <pre>{{ JSON.stringify(uploadResult, null, 2) }}</pre>
        </div>
        
        
        <div v-else-if="aiResult" class="ai-result">
          <h3>KI-Analyse:</h3>
          <div class="ai-provider">
            <strong>Anbieter:</strong> {{ aiResult.provider }}
            <span v-if="aiResult.model">({{ aiResult.model }})</span>
          </div>
          
          <div v-if="aiResult.error" class="ai-error">
            <strong>Fehler:</strong> {{ aiResult.error }}
          </div>
          
          <div v-else-if="aiResult.response" class="ai-response">
            <strong>Analyse:</strong>
            <p>{{ aiResult.response }}</p>
          </div>
        </div>
        
      </div>
    </div>
  </main>
</template>

<style scoped>
.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin: 2rem auto;
}

.upload-result, .ai-result {
  max-width: 600px;
  padding: 1rem;
  background-color: #f8f9fa;
  color: #2c3e50;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.upload-result pre {
  background-color: #eee;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.9rem;
}

.ai-provider {
  margin-bottom: 0.5rem;
  color: #6c757d;
}

.ai-error {
  padding: 0.5rem;
  background-color: #f8d7da;
  color: #721c24;
  border-radius: 4px;
  margin: 0.5rem 0;
}

.ai-response {
  background-color: #e9f7ef;
  padding: 1rem;
  border-radius: 4px;
  margin: 0.5rem 0;
}

.ai-response p {
  white-space: pre-wrap;
  margin: 0.5rem 0 0 0;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  border: 6px solid rgba(255, 255, 255, 0.3);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border-top-color: #4DBA87;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: white;
  font-size: 1.2rem;
  margin-top: 1rem;
  font-weight: bold;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.analyze-button {
  padding: 0.75rem 1.5rem;
  background-color: #4DBA87;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
  align-self: center;
}

.analyze-button:hover {
  background-color: #3a9d6e;
}
</style>
