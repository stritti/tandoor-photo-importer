<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const photoRef = ref<HTMLImageElement | null>(null)
const streaming = ref(false)
const width = ref(320)
const height = ref(0)
const stream = ref<MediaStream | null>(null)
const uploadStatus = ref('')
const isUploading = ref(false)

// Emits für Eltern-Komponenten
const emit = defineEmits(['photo-taken', 'photo-uploaded'])

function startCamera() {
  if (!videoRef.value) return

  navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    .then((mediaStream) => {
      stream.value = mediaStream
      if (videoRef.value) {
        videoRef.value.srcObject = mediaStream
        videoRef.value.play()
      }
    })
    .catch((err) => {
      console.error(`Ein Fehler ist aufgetreten: ${err}`)
      alert('Kamerazugriff nicht möglich. Bitte erlauben Sie den Zugriff auf Ihre Kamera.')
    })

  videoRef.value.addEventListener('canplay', () => {
    if (!streaming.value && videoRef.value) {
      height.value = videoRef.value.videoHeight / (videoRef.value.videoWidth / width.value)
      
      if (isNaN(height.value)) {
        height.value = width.value / (4/3)
      }
      
      videoRef.value.setAttribute('width', width.value.toString())
      videoRef.value.setAttribute('height', height.value.toString())
      if (canvasRef.value) {
        canvasRef.value.setAttribute('width', width.value.toString())
        canvasRef.value.setAttribute('height', height.value.toString())
      }
      streaming.value = true
    }
  }, false)
}

function stopCamera() {
  if (stream.value) {
    stream.value.getTracks().forEach(track => {
      track.stop()
    })
    stream.value = null
    streaming.value = false
    if (videoRef.value) {
      videoRef.value.srcObject = null
    }
  }
}

function takePicture() {
  if (width.value && height.value && canvasRef.value && videoRef.value) {
    const context = canvasRef.value.getContext('2d')
    if (context) {
      canvasRef.value.width = width.value
      canvasRef.value.height = height.value
      context.drawImage(videoRef.value, 0, 0, width.value, height.value)
      
      const data = canvasRef.value.toDataURL('image/png')
      if (photoRef.value) {
        photoRef.value.setAttribute('src', data)
        emit('photo-taken', data)
      }
    }
  }
}

async function uploadPicture() {
  if (!photoRef.value || !photoRef.value.getAttribute('src')) {
    alert('Bitte zuerst ein Foto aufnehmen!')
    return
  }

  const imageData = photoRef.value.getAttribute('src')
  isUploading.value = true
  uploadStatus.value = 'Bild wird hochgeladen...'

  try {
    // Konvertieren des Base64-Bildes in einen Blob
    const response = await fetch(imageData as string)
    const blob = await response.blob()
    
    // Erstellen eines FormData-Objekts für den Upload
    const formData = new FormData()
    formData.append('image', blob, 'camera-image.png')
    
    // Senden des Bildes an das Backend
    const uploadResponse = await fetch('/api/upload-image', {
      method: 'POST',
      body: formData
    })
    
    if (!uploadResponse.ok) {
      throw new Error(`HTTP error! status: ${uploadResponse.status}`)
    }
    
    const result = await uploadResponse.json()
    uploadStatus.value = 'Bild erfolgreich hochgeladen!'
    emit('photo-uploaded', result)
  } catch (error) {
    console.error('Fehler beim Hochladen:', error)
    uploadStatus.value = 'Fehler beim Hochladen des Bildes!'
  } finally {
    isUploading.value = false
  }
}

onMounted(() => {
  startCamera()
})

onUnmounted(() => {
  stopCamera()
})

defineExpose({
  takePicture,
  startCamera,
  stopCamera,
  uploadPicture
})
</script>

<template>
  <div class="camera-container">
    <video ref="videoRef" class="camera-video">Video stream nicht verfügbar.</video>
    <div class="camera-controls">
      <button @click="takePicture" class="camera-button">Foto aufnehmen</button>
      <button @click="uploadPicture" class="upload-button" :disabled="isUploading">
        {{ isUploading ? 'Wird hochgeladen...' : 'Foto hochladen' }}
      </button>
    </div>
    <canvas ref="canvasRef" class="camera-canvas"></canvas>
    <div class="camera-output">
      <img ref="photoRef" alt="Das aufgenommene Foto erscheint hier." />
      <p v-if="uploadStatus" class="upload-status" :class="{ 'success': uploadStatus.includes('erfolgreich'), 'error': uploadStatus.includes('Fehler') }">
        {{ uploadStatus }}
      </p>
    </div>
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

.camera-video {
  width: 100%;
  max-width: 320px;
  height: auto;
  background-color: #eee;
  border-radius: 4px;
}

.camera-controls {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}

.camera-button, .upload-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.camera-button {
  background-color: #4DBA87;
  color: white;
}

.camera-button:hover {
  background-color: #3a9d6e;
}

.upload-button {
  background-color: #2c3e50;
  color: white;
}

.upload-button:hover {
  background-color: #1a2530;
}

.upload-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.camera-canvas {
  display: none;
}

.camera-output {
  margin-top: 1rem;
  width: 100%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
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
</style>
