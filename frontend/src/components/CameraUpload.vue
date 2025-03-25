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

async function takePicture() {
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
        
        // Automatisch hochladen, nachdem das Foto aufgenommen wurde
        await uploadPicture()
      }
    }
  }
}

const aiPrompt = ref('Was ist auf diesem Bild zu sehen?')
const isAnalyzing = ref(false)

async function uploadPicture() {
  if (!photoRef.value || !photoRef.value.getAttribute('src')) {
    alert('Bitte zuerst ein Foto aufnehmen!')
    return
  }

  const imageData = photoRef.value.getAttribute('src')
  isUploading.value = true
  isAnalyzing.value = true
  uploadStatus.value = 'Bild wird hochgeladen...'

  try {
    // Konvertieren des Base64-Bildes in einen Blob
    const response = await fetch(imageData as string)
    const blob = await response.blob()
    
    // Erstellen eines FormData-Objekts für den Upload
    const formData = new FormData()
    formData.append('image', blob, 'camera-image.png')
    
    // Hinzufügen der KI-Analyse-Parameter (immer aktiviert)
    formData.append('analyze_with_ai', 'true')
    formData.append('prompt', aiPrompt.value)
    
    // Backend-Basis-URL aus Umgebungsvariablen
    const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || '';
    
    // Senden des Bildes an das Backend
    const uploadResponse = await fetch(`${backendBaseUrl}/api/upload-image`, {
      method: 'POST',
      body: formData
    })
    
    if (!uploadResponse.ok) {
      throw new Error(`HTTP error! status: ${uploadResponse.status}`)
    }
    
    const result = await uploadResponse.json()
    uploadStatus.value = 'Bild erfolgreich hochgeladen!'
    
    // Wenn KI-Analyse nicht direkt durchgeführt wurde
    if (!result.ai_analysis) {
      isAnalyzing.value = true
      uploadStatus.value = 'Analysiere Bild mit KI...'
      
      try {
        const analyzeResponse = await fetch(`${backendBaseUrl}/api/analyze-image`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            image_path: result.path,
            prompt: aiPrompt.value
          })
        })
        
        if (!analyzeResponse.ok) {
          throw new Error(`HTTP error! status: ${analyzeResponse.status}`)
        }
        
        const analyzeResult = await analyzeResponse.json()
        result.ai_analysis = analyzeResult.ai_analysis
        uploadStatus.value = 'Bild erfolgreich analysiert!'
      } catch (analyzeError) {
        console.error('Fehler bei der KI-Analyse:', analyzeError)
        uploadStatus.value = 'Fehler bei der KI-Analyse!'
        result.ai_analysis_error = true
      } finally {
        isAnalyzing.value = false
      }
    }
    
    emit('photo-uploaded', result)
  } catch (error) {
    console.error('Fehler beim Hochladen:', error)
    uploadStatus.value = 'Fehler beim Hochladen des Bildes!'
  } finally {
    isUploading.value = false
  }
}

async function analyzeExistingImage(imagePath: string) {
  if (!imagePath) return
  
  isAnalyzing.value = true
  uploadStatus.value = 'Analysiere Bild mit KI...'
  
  try {
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
    })
    
    if (!analyzeResponse.ok) {
      throw new Error(`HTTP error! status: ${analyzeResponse.status}`)
    }
    
    const result = await analyzeResponse.json()
    uploadStatus.value = 'Bild erfolgreich analysiert!'
    emit('photo-analyzed', result)
    return result
  } catch (error) {
    console.error('Fehler bei der KI-Analyse:', error)
    uploadStatus.value = 'Fehler bei der KI-Analyse!'
    throw error
  } finally {
    isAnalyzing.value = false
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
  uploadPicture,
  analyzeExistingImage
})
</script>

<template>
  <div class="camera-container">
    <video ref="videoRef" class="camera-video">Video stream nicht verfügbar.</video>
    <div class="camera-controls">
      <button @click="takePicture" class="camera-button" :disabled="isUploading || isAnalyzing">
        {{ isUploading ? 'Wird verarbeitet...' : 'Foto aufnehmen und analysieren' }}
      </button>
    </div>
    
    <div class="ai-options">
      <div class="ai-prompt">
        <label for="ai-prompt">Anweisung für KI:</label>
        <input 
          type="text" 
          id="ai-prompt" 
          v-model="aiPrompt" 
          placeholder="Was ist auf diesem Bild zu sehen?"
        />
      </div>
    </div>
    
    <canvas ref="canvasRef" class="camera-canvas"></canvas>
    <div class="camera-output">
      <img ref="photoRef" alt="Das aufgenommene Foto erscheint hier." />
      <p v-if="uploadStatus" class="upload-status" :class="{ 
        'success': uploadStatus.includes('erfolgreich'), 
        'error': uploadStatus.includes('Fehler'),
        'info': uploadStatus.includes('Analysiere') || uploadStatus.includes('hochgeladen')
      }">
        {{ uploadStatus }}
        <div v-if="isUploading || isAnalyzing" class="spinner-container">
          <div class="spinner"></div>
        </div>
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

.info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.ai-options {
  margin: 1rem 0;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  width: 100%;
  max-width: 320px;
}

.ai-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.ai-checkbox label {
  margin-left: 0.5rem;
  cursor: pointer;
}

.ai-prompt {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ai-prompt input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
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
