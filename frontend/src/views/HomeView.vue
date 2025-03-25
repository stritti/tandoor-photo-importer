<script setup lang="ts">
import { ref } from 'vue'
import CameraUpload from '@/components/CameraUpload.vue'

const uploadResult = ref<any>(null)
const aiResult = ref<any>(null)
const cameraUploadRef = ref<InstanceType<typeof CameraUpload> | null>(null)

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
  }
}

async function analyzeImage() {
  if (!uploadResult.value || !uploadResult.value.path) {
    alert('Bitte zuerst ein Foto hochladen!')
    return
  }
  
  try {
    if (cameraUploadRef.value) {
      const result = await cameraUploadRef.value.analyzeExistingImage(uploadResult.value.path)
      aiResult.value = result.ai_analysis
    }
  } catch (error) {
    console.error('Fehler bei der Analyse:', error)
  }
}
</script>

<template>
  <main>
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
        
        <div v-if="uploadResult && !aiResult" class="ai-result loading">
          <h3>KI-Analyse wird geladen...</h3>
          <div class="spinner-container">
            <div class="spinner"></div>
          </div>
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

.spinner-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: #4DBA87;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.ai-result.loading {
  background-color: #f0f7ff;
  text-align: center;
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
