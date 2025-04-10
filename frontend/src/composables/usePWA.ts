import { ref, onMounted, onUnmounted } from 'vue'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export function usePWA() {
  const isInstallable = ref(false)
  const isOffline = ref(!navigator.onLine)
  let deferredPrompt: BeforeInstallPromptEvent | null = null

  // Prüfen, ob die App installierbar ist
  const handleBeforeInstallPrompt = (e: Event) => {
    // Verhindern, dass der Browser seinen eigenen Dialog zeigt
    e.preventDefault()
    // Speichern des Events für späteren Gebrauch
    deferredPrompt = e as BeforeInstallPromptEvent
    // Anzeigen des eigenen Install-Banners
    isInstallable.value = true
  }

  // App installieren, wenn der Benutzer auf den Button klickt
  const installApp = async () => {
    if (!deferredPrompt) return

    // Installation-Dialog anzeigen
    deferredPrompt.prompt()

    // Warten auf die Entscheidung des Benutzers
    const { outcome } = await deferredPrompt.userChoice

    // Wenn der Benutzer die Installation akzeptiert hat
    if (outcome === 'accepted') {
      console.log('App wurde installiert')
    } else {
      console.log('Installation abgelehnt')
    }

    // Das Event kann nur einmal verwendet werden
    deferredPrompt = null
    isInstallable.value = false
  }

  // Online/Offline-Status überwachen
  const handleOnlineStatus = () => {
    isOffline.value = !navigator.onLine
  }

  onMounted(() => {
    // Event-Listener für die Installation hinzufügen
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    
    // Online/Offline-Status überwachen
    window.addEventListener('online', handleOnlineStatus)
    window.addEventListener('offline', handleOnlineStatus)
  })

  onUnmounted(() => {
    // Event-Listener entfernen
    window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.removeEventListener('online', handleOnlineStatus)
    window.removeEventListener('offline', handleOnlineStatus)
  })

  return {
    isInstallable,
    installApp,
    isOffline
  }
}
