import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { createAppRouter } from './router/index'
import { setUnauthorizedHandler } from './api/index'
import { useAuthStore } from './stores/auth'
import { useToastStore } from './stores/toast'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
const router = createAppRouter()
app.use(pinia)
app.use(router)

// Session expirée pendant l'utilisation : retour à l'écran de connexion.
setUnauthorizedHandler(() => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) return
  auth.clearSession()
  useToastStore().info('Votre session a expiré, reconnectez-vous.')
  router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
})

// Filet de sécurité : aucune erreur inattendue ne passe inaperçue.
app.config.errorHandler = (err) => {
  console.error(err)
  useToastStore().error(err)
}

app.mount('#app')
