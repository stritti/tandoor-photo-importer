<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useImageAnalysisStore } from '../stores/imageAnalysisStore'

const store = useImageAnalysisStore()

const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const streaming = ref(false)
const width = ref(320)
const height = ref(0)
const stream = ref<MediaStream | null>(null)

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
      store.setCurrentImageData(data)
      
      // Bild aus DataURL in File-Objekt umwandeln
      const byteString = atob(data.split(',')[1])
      const mimeString = data.split(',')[0].split(':')[1].split(';')[0]
      const ab = new ArrayBuffer(byteString.length)
      const ia = new Uint8Array(ab)
      
      for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i)
      }
      
      const blob = new Blob([ab], { type: mimeString })
      const file = new File([blob], "camera-image.png", { type: "image/png" })
      
      // Bild hochladen und analysieren
      store.uploadAndAnalyzeImage(file)
    }
  }
}

onMounted(() => {
  startCamera()
})

onUnmounted(() => {
  stopCamera()
})

defineExpose({
  startCamera,
  stopCamera,
  takePicture
})
</script>

<template>
  <div>
    <video ref="videoRef" class="camera-video">Video stream nicht verfügbar.</video>
    <div class="camera-controls">
      <button @click="takePicture" class="camera-button" :disabled="store.isUploading || store.isAnalyzing">
        {{ store.isUploading || store.isAnalyzing ? 'Wird verarbeitet...' : 'Foto aufnehmen und analysieren' }}
      </button>
    </div>
    <canvas ref="canvasRef" class="camera-canvas"></canvas>
  </div>
</template>

<style scoped>
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

.camera-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
  background-color: #4DBA87;
  color: white;
}

.camera-button:hover {
  background-color: #3a9d6e;
}

.camera-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.camera-canvas {
  display: none;
}
</style>
