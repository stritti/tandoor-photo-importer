<template>
  <div id="app">
    <h1>{{ title }}</h1>
    <div v-if="loading">Lade Daten...</div>
    <div v-else>
      <div v-if="error">{{ error }}</div>
      <div v-else>
        <p>{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      title: 'Vue.js + Flask Demo',
      message: '',
      loading: true,
      error: null
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        this.loading = true;
        const response = await axios.get('/api/hello');
        this.message = response.data.message;
        this.error = null;
      } catch (err) {
        this.error = 'Fehler beim Laden der Daten: ' + err.message;
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
