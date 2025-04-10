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
const availableCameras = ref<MediaDeviceInfo[]>([])
const selectedCameraId = ref<string | null>(null)

async function getCameraList() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    availableCameras.value = devices.filter(device => device.kind === 'videoinput')
    if (availableCameras.value.length > 0 && !selectedCameraId.value) {
      // Optional: Wähle die erste Kamera standardmäßig aus, wenn keine ausgewählt ist
      // selectedCameraId.value = availableCameras.value[0].deviceId;
    }
  } catch (err) {
    console.error("Fehler beim Auflisten der Kameras: ", err)
  }
}

async function startCamera() {
  if (streaming.value) {
    stopCamera() // Stoppe den aktuellen Stream, bevor ein neuer gestartet wird
  }
  if (!videoRef.value) return

  const constraints: MediaStreamConstraints = {
    video: selectedCameraId.value
      ? { deviceId: { exact: selectedCameraId.value } }
      : { facingMode: 'environment' }, // Standardmäßig Rückkamera
    audio: false
  }

  try {
    const mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
    stream.value = mediaStream
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      videoRef.value.play()
      // Rufe die Kameraliste erneut auf, um sicherzustellen, dass die Labels verfügbar sind
      await getCameraList()
    }
  } catch (err) {
    console.error(`Ein Fehler ist aufgetreten: ${err}`)
    alert('Kamerazugriff nicht möglich. Bitte erlauben Sie den Zugriff auf Ihre Kamera oder wählen Sie eine andere Kamera aus.')
    // Setze die Auswahl zurück, falls die ausgewählte Kamera fehlschlägt
    if (selectedCameraId.value) {
      selectedCameraId.value = null;
      await startCamera(); // Versuche es erneut mit der Standardkamera
    }
  }
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
    console.log("Stopping camera stream");
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

async function switchCamera(event: Event) {
  const target = event.target as HTMLSelectElement;
  const deviceId = target.value;
  if (deviceId && deviceId !== selectedCameraId.value) {
    selectedCameraId.value = deviceId;
    await startCamera(); // Starte die Kamera mit der neuen ID neu
  }
}

function takePicture() {
  if (width.value && height.value && canvasRef.value && videoRef.value && streaming.value) {
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

onMounted(async () => {
  await getCameraList() // Versuche, die Liste vor dem Start zu laden
  await startCamera()
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
    <video ref="videoRef" class="camera-video" autoplay playsinline>Video stream nicht verfügbar.</video>
    <div class="camera-controls">
      <div v-if="availableCameras.length > 1" class="camera-select-wrapper">
        <label for="camera-select">Kamera:</label>
        <select id="camera-select" :value="selectedCameraId" @change="switchCamera" class="camera-select">
          <option :value="null">Standard</option>
          <option v-for="camera in availableCameras" :key="camera.deviceId" :value="camera.deviceId">
            {{ camera.label || `Kamera ${availableCameras.indexOf(camera) + 1}` }}
          </option>
        </select>
      </div>
      <button @click="takePicture" class="camera-button" :disabled="!streaming || store.isUploading || store.isAnalyzing">
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
  align-items: center; /* Zentriert Elemente vertikal */
}

.camera-select-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.camera-select {
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  border: 1px solid #ccc;
  background-color: white;
  cursor: pointer;
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
