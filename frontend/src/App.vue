<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { ref } from 'vue'
import CameraUpload from './components/CameraUpload.vue'

const showCamera = ref(false)
const capturedPhoto = ref('')
const uploadResult = ref<any>(null)

function toggleCamera() {
  showCamera.value = !showCamera.value
}

function handlePhotoTaken(photoData: string) {
  capturedPhoto.value = photoData
  console.log('Foto aufgenommen!')
}

function handlePhotoUploaded(result: any) {
  uploadResult.value = result
  console.log('Foto hochgeladen!', result)
}
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="You did it!" />

      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
        <button @click="toggleCamera" class="camera-button">
          {{ showCamera ? 'Kamera ausschalten' : 'Kamera einschalten' }}
        </button>
      </nav>
    </div>
  </header>

  <CameraUpload 
    v-if="showCamera" 
    @photo-taken="handlePhotoTaken" 
    @photo-uploaded="handlePhotoUploaded" 
  />

  <div v-if="uploadResult" class="upload-result">
    <h3>Upload-Ergebnis:</h3>
    <pre>{{ JSON.stringify(uploadResult, null, 2) }}</pre>
  </div>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

.camera-button {
  display: inline-block;
  margin-left: 1rem;
  padding: 0.5rem 1rem;
  background-color: #4DBA87;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.upload-result {
  margin: 2rem auto;
  max-width: 600px;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.upload-result pre {
  background-color: #eee;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
