<template>
  <RouterView v-if="route.meta.guest" />
  <div
    v-else-if="auth.isAuthenticated"
    class="flex h-screen bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-100 overflow-hidden"
  >
    <Sidebar />
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">
      <RouterView />
    </div>
  </div>
  <div v-else class="h-screen flex items-center justify-center bg-slate-100 dark:bg-slate-900">
    <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
  </div>

  <ToastContainer />
  <ConfirmDialog />
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import ToastContainer from './components/ToastContainer.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import { useDarkMode } from './composables/useDarkMode'
import { useAuthStore } from './stores/auth'
import { useClientStore } from './stores/clientStore'
import { useTaskStore } from './stores/taskStore'

useDarkMode()
const route = useRoute()
const auth = useAuthStore()
const clientStore = useClientStore()
const taskStore = useTaskStore()

// Changement de compte : on recharge les clients, et on vide tout à la déconnexion.
watch(
  () => auth.user?.id,
  (userId) => {
    if (userId) {
      clientStore.fetchAll()
    } else {
      clientStore.reset()
      taskStore.reset()
    }
  },
  { immediate: true },
)
</script>
