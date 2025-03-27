<script setup lang="ts">
import { ref, watch } from 'vue'
import CameraUpload from '@/components/CameraUpload.vue'

interface UploadResult {
  path?: string;
  ai_analysis?: AIResult;
  [key: string]: unknown;
}

interface AIResult {
  provider: string;
  model?: string;
  response?: string;
  error?: string;
}

interface ImportResult {
  success: boolean;
  recipe_url?: string;
  error?: string;
}

const uploadResult = ref<UploadResult | null>(null)
const aiResult = ref<AIResult | null>(null)
const cameraUploadRef = ref<InstanceType<typeof CameraUpload> | null>(null)
const isLoading = ref(false)
const jsonLdData = ref<Record<string, unknown> | null>(null)
const isImporting = ref(false)
const importResult = ref<ImportResult | null>(null)

// Tandoor Auth
const showAuthForm = ref(false)
const username = ref('')
const password = ref('')
import { useSessionStorage } from '@vueuse/core'

const authToken = useSessionStorage('tandoorAuthToken', '')
const isAuthenticating = ref(false)
const authError = ref('')

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function handlePhotoTaken(_photoData: string): void {
  console.log('Foto aufgenommen!')
  // Zurücksetzen der Ergebnisse bei neuem Foto
  uploadResult.value = null
  aiResult.value = null
}

function handlePhotoUploaded(result: UploadResult) {
  uploadResult.value = result
  console.log('Foto hochgeladen!', result)

  // Wenn KI-Analyse vorhanden ist, extrahieren
  if (result.ai_analysis) {
    aiResult.value = result.ai_analysis
  }

  // Immer den Loading-Status zurücksetzen, wenn Ergebnisse zurückkommen
  isLoading.value = false
}


// Extrahiert JSON-LD aus der KI-Antwort
async function extractJsonLd() {
  if (!aiResult.value || !aiResult.value.response) return

  isLoading.value = true
  try {
    const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || '';
    const response = await fetch(`${backendBaseUrl}/api/extract-json-ld`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ai_response: aiResult.value.response
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    if (result.success) {
      jsonLdData.value = result.json_ld
    } else {
      alert(result.error || 'Fehler beim Extrahieren des JSON-LD')
    }
  } catch (error) {
    console.error('Fehler beim Extrahieren des JSON-LD:', error)
    alert('Fehler beim Extrahieren des JSON-LD')
  } finally {
    isLoading.value = false
  }
}

// Authentifiziert bei Tandoor
async function authenticateTandoor() {
  if (!username.value || !password.value) {
    authError.value = 'Bitte Benutzername und Passwort eingeben'
    return
  }

  isAuthenticating.value = true
  authError.value = ''

  try {
    const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || '';
    const response = await fetch(`${backendBaseUrl}/api/tandoor-auth`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })

    const result = await response.json()

    if (response.ok && result.success) {
      authToken.value = result.token
      showAuthForm.value = false
      // Nach erfolgreicher Authentifizierung direkt importieren
      await importToTandoor()
    } else {
      authError.value = result.error || 'Authentifizierung fehlgeschlagen'
    }
  } catch (error) {
    console.error('Fehler bei der Authentifizierung:', error)
    authError.value = 'Fehler bei der Verbindung zum Server'
  } finally {
    isAuthenticating.value = false
  }
}

// Importiert das Rezept in Tandoor
async function importToTandoor() {
  if (!jsonLdData.value) return

  if (!authToken.value) {
    // Wenn kein Token vorhanden ist, Authentifizierungsformular anzeigen
    showAuthForm.value = true
    return
  }

  isImporting.value = true
  importResult.value = null

  try {
    const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || '';
    const response = await fetch(`${backendBaseUrl}/api/import-to-tandoor`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        recipe_json_ld: jsonLdData.value,
        auth_token: authToken.value
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    importResult.value = await response.json()
  } catch (error) {
    console.error('Fehler beim Import in Tandoor:', error)
    importResult.value = {
      success: false,
      error: 'Fehler beim Import in Tandoor'
    }
  } finally {
    isImporting.value = false
  }
}

// Wenn aiResult gesetzt wird, Loading-Status zurücksetzen und JSON-LD zurücksetzen
watch(aiResult, (newValue) => {
  if (newValue) {
    isLoading.value = false
    jsonLdData.value = null
    importResult.value = null
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
        :prompt="aiPrompt"
      />

      <div v-if="uploadResult" class="result-container">
        <div class="upload-result">
          <h3>Upload-Ergebnis:</h3>
          <pre>{{ JSON.stringify(uploadResult, null, 2) }}</pre>
        </div>

        <div v-if="aiResult" class="ai-result">
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

            <div v-if="jsonLdData" class="json-ld-container">
              <h4>Extrahiertes Rezept:</h4>
              <pre>{{ JSON.stringify(jsonLdData, null, 2) }}</pre>
              <button @click="importToTandoor" class="import-button" :disabled="isImporting">
                {{ isImporting ? 'Wird importiert...' : 'In Tandoor importieren' }}
              </button>
              <div v-if="importResult" class="import-result" :class="{ 'success': importResult.success }">
                <p v-if="importResult.success">
                  Rezept erfolgreich importiert!
                  <a :href="importResult.recipe_url" target="_blank">Rezept in Tandoor öffnen</a>
                </p>
                <p v-else>Fehler beim Import: {{ importResult.error }}</p>
              </div>
            </div>

            <button v-if="!jsonLdData && aiResult.response.includes('```json')" @click="extractJsonLd" class="extract-button">
              JSON-LD extrahieren
            </button>
          </div>
        </div>

        <!-- Tandoor Auth Modal -->
        <div v-if="showAuthForm" class="auth-modal">
          <div class="auth-modal-content">
            <h3>Tandoor Anmeldung</h3>
            <p>Bitte geben Sie Ihre Tandoor-Anmeldedaten ein, um das Rezept zu importieren.</p>

            <div class="auth-form">
              <div class="form-group">
                <label for="username">Benutzername:</label>
                <input type="text" id="username" v-model="username" placeholder="Benutzername" />
              </div>

              <div class="form-group">
                <label for="password">Passwort:</label>
                <input type="password" id="password" v-model="password" placeholder="Passwort" />
              </div>

              <div v-if="authError" class="auth-error">{{ authError }}</div>

              <div class="auth-buttons">
                <button @click="showAuthForm = false" class="cancel-button">Abbrechen</button>
                <button @click="authenticateTandoor" class="login-button" :disabled="isAuthenticating">
                  {{ isAuthenticating ? 'Anmelden...' : 'Anmelden & Importieren' }}
                </button>
              </div>
            </div>
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
  color: #d0d0d0;
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

.json-ld-container {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f0f7ff;
  border-radius: 4px;
}

.json-ld-container pre {
  background-color: #eee;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.9rem;
  max-height: 300px;
}

.extract-button, .import-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #4DBA87;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.extract-button:hover, .import-button:hover {
  background-color: #3a9d6e;
}

.extract-button:disabled, .import-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.import-result {
  margin-top: 1rem;
  padding: 0.5rem;
  border-radius: 4px;
  background-color: #f8d7da;
  color: #721c24;
}

.import-result.success {
  background-color: #d4edda;
  color: #155724;
}

.import-result a {
  color: #0056b3;
  text-decoration: none;
  font-weight: bold;
}

.import-result a:hover {
  text-decoration: underline;
}

/* Auth Modal Styles */
.auth-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.auth-modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: bold;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.auth-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-button {
  padding: 0.5rem 1rem;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login-button {
  padding: 0.5rem 1rem;
  background-color: #4DBA87;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
}

.auth-error {
  color: #721c24;
  background-color: #f8d7da;
  padding: 0.5rem;
  border-radius: 4px;
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
