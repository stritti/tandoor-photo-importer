<script setup lang="ts">
import { useImageAnalysisStore } from '../stores/imageAnalysisStore'

const store = useImageAnalysisStore()

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  if (!target.files || target.files.length === 0) return;

  const file = target.files[0];

  // Datei als DataURL lesen
  const reader = new FileReader();
  reader.onload = (e) => {
    if (e.target) {
      const dataUrl = e.target.result as string;
      store.setCurrentImageData(dataUrl);
      store.uploadAndAnalyzeImage(file);
    }
  };
  reader.readAsDataURL(file);
}
</script>

<template>
  <div class="upload-container">
    <input
      type="file"
      id="file-upload"
      accept="image/*"
      @change="handleFileUpload"
      class="file-input"
    >
    <label for="file-upload" class="file-upload-button" :class="{ disabled: store.isUploading || store.isAnalyzing }">
      {{ store.isUploading || store.isAnalyzing ? 'Wird verarbeitet...' : 'Foto auswählen' }}
    </label>
    <p class="upload-hint">Tippen Sie auf den Button, um ein Foto aus Ihrer Mediathek auszuwählen</p>
  </div>
</template>

<style scoped>
.upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.file-input {
  display: none;
}

.file-upload-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background-color: #4DBA87;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  text-align: center;
  transition: background-color 0.3s;
}

.file-upload-button:hover {
  background-color: #3a9d6e;
}

.file-upload-button.disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.upload-hint {
  margin-top: 1rem;
  color: #6c757d;
  font-size: 0.9rem;
  text-align: center;
}
</style>
