<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import CameraTab from './CameraTab.vue'
import UploadTab from './UploadTab.vue'
import PhotoPreview from './PhotoPreview.vue'
import { usePWA } from '../composables/usePWA'

// PWA-Funktionalität
const { isInstallable, installApp, isOffline } = usePWA()

// Emits für Eltern-Komponenten
const props = defineProps<{
  prompt: string
}>()

const emit = defineEmits(['photo-taken', 'photo-uploaded'])

// Zustandsvariablen
const uploadStatus = ref('')
const isUploading = ref(false)
const isAnalyzing = ref(false)
const activeTab = ref('camera') // 'camera' oder 'upload'
const aiPrompt = ref('Was ist auf diesem Bild zu sehen?')

// Komponenten-Referenzen
const cameraTabRef = ref<InstanceType<typeof CameraTab> | null>(null)
const photoPreviewRef = ref<InstanceType<typeof PhotoPreview> | null>(null)

// Wenn der Tab wechselt, Kamera entsprechend starten oder stoppen
watch(activeTab, (newTab) => {
  if (newTab === 'camera' && cameraTabRef.value) {
    cameraTabRef.value.startCamera();
  } else if (cameraTabRef.value) {
    cameraTabRef.value.stopCamera();
  }
});

// Handler für Foto-Aufnahme
async function handlePhotoTaken(dataUrl: string) {
  if (photoPreviewRef.value?.photoRef) {
    photoPreviewRef.value.photoRef.setAttribute('src', dataUrl);
    emit('photo-taken', dataUrl);
    
    // Automatisch hochladen
    await uploadPicture();
  }
}

// Handler für Datei-Auswahl
async function handleFileSelected(data: { dataUrl: string, file: File }) {
  if (photoPreviewRef.value?.photoRef) {
    photoPreviewRef.value.photoRef.setAttribute('src', data.dataUrl as string);
    emit('photo-taken', data.dataUrl);
    
    // Automatisch hochladen
    await uploadPicture(data.file);
  }
}

async function uploadPicture(imageFile?: File) {
  if (!photoPreviewRef.value?.photoRef || 
      !photoPreviewRef.value.photoRef.getAttribute('src')) {
    alert('Bitte zuerst ein Foto aufnehmen oder auswählen!');
    return;
  }

  isUploading.value = true;
  isAnalyzing.value = true;
  uploadStatus.value = 'Bild wird hochgeladen...';

  try {
    let blob: Blob;

    if (imageFile) {
      // Verwende die übergebene Datei direkt
      blob = imageFile;
    } else {
      // Konvertieren des Base64-Bildes in einen Blob
      const imageData = photoPreviewRef.value.photoRef.getAttribute('src') as string;
      const response = await fetch(imageData);
      blob = await response.blob();
    }

    // Erstellen eines FormData-Objekts für den Upload
    const formData = new FormData();
    formData.append('image', blob, 'camera-image.png');

    // Hinzufügen der KI-Analyse-Parameter
    formData.append('analyze_with_ai', 'true');
    formData.append('prompt', props.prompt);

    // Backend-Basis-URL aus Umgebungsvariablen
    const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || '';

    // Senden des Bildes an das Backend
    const uploadResponse = await fetch(`${backendBaseUrl}/api/upload-image`, {
      method: 'POST',
      body: formData
    });

    if (!uploadResponse.ok) {
      throw new Error(`HTTP error! status: ${uploadResponse.status}`);
    }

    const result = await uploadResponse.json();
    uploadStatus.value = 'Bild erfolgreich hochgeladen!';

    // Spinner beenden, sobald die Antwort zurückkommt
    isUploading.value = false;
    isAnalyzing.value = false;

    // Wenn KI-Analyse nicht direkt durchgeführt wurde
    if (!result.ai_analysis) {
      isAnalyzing.value = true;
      uploadStatus.value = 'Analysiere Bild mit KI...';

      try {
        const analyzeResult = await analyzeImage(result.path);
        result.ai_analysis = analyzeResult.ai_analysis;
        uploadStatus.value = 'Bild erfolgreich analysiert!';
      } catch (analyzeError) {
        console.error('Fehler bei der KI-Analyse:', analyzeError);
        uploadStatus.value = 'Fehler bei der KI-Analyse!';
        result.ai_analysis_error = true;
      } finally {
        isAnalyzing.value = false;
      }
    }

    emit('photo-uploaded', result);
  } catch (error) {
    console.error('Fehler beim Hochladen:', error);
    uploadStatus.value = 'Fehler beim Hochladen des Bildes!';
  } finally {
    isUploading.value = false;
  }
}

async function analyzeImage(imagePath: string) {
  const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || '';
  const analyzeResponse = await fetch(`${backendBaseUrl}/api/analyze-image`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image_path: imagePath,
      prompt: aiPrompt.value
    })
  });

  if (!analyzeResponse.ok) {
    throw new Error(`HTTP error! status: ${analyzeResponse.status}`);
  }

  return await analyzeResponse.json();
}

async function analyzeExistingImage(imagePath: string) {
  if (!imagePath) return;

  isAnalyzing.value = true;
  uploadStatus.value = 'Analysiere Bild mit KI...';

  try {
    const result = await analyzeImage(imagePath);
    uploadStatus.value = 'Bild erfolgreich analysiert!';
    return result;
  } catch (error) {
    console.error('Fehler bei der KI-Analyse:', error);
    uploadStatus.value = 'Fehler bei der KI-Analyse!';
    throw error;
  } finally {
    isAnalyzing.value = false;
  }
}

defineExpose({
  uploadPicture,
  analyzeExistingImage
});
</script>

<template>
  <div class="camera-container">
    <!-- PWA Installation Banner -->
    <div v-if="isInstallable" class="pwa-install-banner">
      <p>Installieren Sie diese App auf Ihrem Gerät für eine bessere Erfahrung!</p>
      <button @click="installApp" class="install-button">Installieren</button>
    </div>

    <!-- Offline-Hinweis -->
    <div v-if="isOffline" class="offline-banner">
      <p>Sie sind offline. Einige Funktionen sind möglicherweise eingeschränkt.</p>
    </div>

    <div class="camera-tabs">
      <button
        @click="activeTab = 'camera'"
        :class="{ active: activeTab === 'camera' }"
        class="tab-button"
      >
        Kamera
      </button>
      <button
        @click="activeTab = 'upload'"
        :class="{ active: activeTab === 'upload' }"
        class="tab-button"
      >
        Foto auswählen
      </button>
    </div>

    <CameraTab 
      v-if="activeTab === 'camera'" 
      ref="cameraTabRef"
      :isUploading="isUploading"
      :isAnalyzing="isAnalyzing"
      @photo-taken="handlePhotoTaken"
    />

    <UploadTab 
      v-else-if="activeTab === 'upload'"
      :isUploading="isUploading"
      :isAnalyzing="isAnalyzing"
      @file-selected="handleFileSelected"
    />

    <PhotoPreview 
      ref="photoPreviewRef"
      :uploadStatus="uploadStatus"
      :isUploading="isUploading"
      :isAnalyzing="isAnalyzing"
    />
  </div>
</template>

<style scoped>
.camera-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 2rem auto;
  max-width: 800px;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
}

.camera-tabs {
  display: flex;
  margin-bottom: 1rem;
  border-bottom: 1px solid #ddd;
}

.tab-button {
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: bold;
  color: #6c757d;
  border-bottom: 3px solid transparent;
}

.tab-button.active {
  color: #4DBA87;
  border-bottom: 3px solid #4DBA87;
}

.pwa-install-banner {
  width: 100%;
  padding: 0.75rem;
  background-color: #d1ecf1;
  color: #0c5460;
  border-radius: 4px;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.install-button {
  padding: 0.5rem 1rem;
  background-color: #4DBA87;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.offline-banner {
  width: 100%;
  padding: 0.75rem;
  background-color: #fff3cd;
  color: #856404;
  border-radius: 4px;
  margin-bottom: 1rem;
  text-align: center;
}
</style>
