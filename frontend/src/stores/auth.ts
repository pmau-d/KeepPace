import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '../api/index'
import type { RegisterPayload, User } from '../types/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
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

  async function login(email: string, password: string) {
    user.value = (await authApi.login({ email, password })).data
    checked.value = true
  }

  async function register(payload: RegisterPayload) {
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
