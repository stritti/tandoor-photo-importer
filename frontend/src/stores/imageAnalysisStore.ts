import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useImageAnalysisStore = defineStore('imageAnalysis', () => {
  // Status-Variablen
  const isUploading = ref(false)
  const isAnalyzing = ref(false)
  const uploadStatus = ref('')
  const analysisResult = ref('')
  
  // Bild-Daten
  const currentImageData = ref('')
  
  // Funktionen
  function setUploading(status: boolean) {
    isUploading.value = status
  }
  
  function setAnalyzing(status: boolean) {
    isAnalyzing.value = status
  }
  
  function setUploadStatus(status: string) {
    uploadStatus.value = status
  }
  
  function setAnalysisResult(result: string) {
    analysisResult.value = result
  }
  
  function setCurrentImageData(data: string) {
    currentImageData.value = data
  }
  
  async function uploadAndAnalyzeImage(file: File) {
    try {
      setUploading(true)
      setUploadStatus('Bild wird hochgeladen...')
      
      const formData = new FormData()
      formData.append('file', file)
      
      // Optional: Prompt-Typ hinzufügen
      // formData.append('prompt_type', 'general')
      
      const response = await fetch('/api/upload-image', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error(`HTTP Fehler: ${response.status}`)
      }
      
      setUploading(false)
      setUploadStatus('Bild erfolgreich hochgeladen. Analysiere...')
      setAnalyzing(true)
      
      const data = await response.json()
      
      setAnalyzing(false)
      setAnalysisResult(data.analysis)
      setUploadStatus('Analyse erfolgreich abgeschlossen.')
    } catch (error) {
      setUploading(false)
      setAnalyzing(false)
      setUploadStatus(`Fehler: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`)
      console.error('Fehler beim Hochladen/Analysieren:', error)
    }
  }
  
  function reset() {
    isUploading.value = false
    isAnalyzing.value = false
    uploadStatus.value = ''
    analysisResult.value = ''
    currentImageData.value = ''
  }

  return { 
    isUploading, 
    isAnalyzing, 
    uploadStatus, 
    analysisResult,
    currentImageData,
    setUploading,
    setAnalyzing,
    setUploadStatus,
    setAnalysisResult,
    setCurrentImageData,
    uploadAndAnalyzeImage,
    reset
  }
})
