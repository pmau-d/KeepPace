<template>
  <header
    class="border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/70 backdrop-blur-sm"
  >
    <div class="max-w-5xl mx-auto px-5 h-14 flex items-center justify-between">
      <RouterLink :to="{ name: 'public-projects' }" class="flex items-center gap-2.5">
        <AppLogo size="sm" />
        <span class="font-bold text-slate-800 dark:text-white">KeepPace</span>
      </RouterLink>
      <RouterLink
        :to="auth.isAuthenticated ? { name: 'tasks' } : { name: 'login' }"
        class="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
      >
        {{ auth.isAuthenticated ? 'Mon espace' : 'Se connecter' }}
      </RouterLink>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import AppLogo from './AppLogo.vue'

const auth = useAuthStore()
</script>
