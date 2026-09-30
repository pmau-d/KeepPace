import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '../api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  // Vrai une fois la session vérifiée auprès de l'API (connecté ou non).
  const checked = ref(false)
  const isAuthenticated = computed(() => user.value !== null)

  async function fetchMe() {
    try {
      user.value = (await authApi.me()).data
    } catch {
      user.value = null
    } finally {
      checked.value = true
    }
    return user.value
  }

  async function login(email, password) {
    user.value = (await authApi.login({ email, password })).data
    checked.value = true
  }

  async function register(payload) {
    user.value = (await authApi.register(payload)).data
    checked.value = true
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearSession()
    }
  }

  function clearSession() {
    user.value = null
  }

  return { user, checked, isAuthenticated, fetchMe, login, register, logout, clearSession }
})
