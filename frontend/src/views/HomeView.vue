<script setup lang="ts">
import { ref } from 'vue'
import CameraUpload from '@/components/CameraUpload.vue'

const uploadResult = ref<any>(null)

function handlePhotoTaken(photoData: string) {
  console.log('Foto aufgenommen!')
}

function handlePhotoUploaded(result: any) {
  uploadResult.value = result
  console.log('Foto hochgeladen!', result)
}
</script>

<template>
  <main>
    <div class="app-container">
      <h1>Kamera App</h1>
      
      <CameraUpload 
        @photo-taken="handlePhotoTaken" 
        @photo-uploaded="handlePhotoUploaded" 
      />

      <div v-if="uploadResult" class="upload-result">
        <h3>Upload-Ergebnis:</h3>
        <pre>{{ JSON.stringify(uploadResult, null, 2) }}</pre>
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

.upload-result {
  margin: 2rem auto;
  max-width: 600px;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.upload-result pre {
  background-color: #eee;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
