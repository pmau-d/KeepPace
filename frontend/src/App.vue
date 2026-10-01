<template>
  <RouterView v-if="route.meta.guest" />
  <div
    v-else-if="auth.isAuthenticated"
    class="flex h-screen bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-100 overflow-hidden"
  >
    <Sidebar />
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">
      <!-- Petit écran : la barre latérale devient un tiroir ouvert depuis cette barre -->
      <div
        class="lg:hidden flex items-center gap-3 px-4 py-2.5 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shrink-0"
      >
        <button
          type="button"
          class="p-1.5 -ml-1.5 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
          aria-label="Ouvrir le menu"
          :aria-expanded="drawerOpen"
          @click="openDrawer"
        >
          <Menu class="w-5 h-5" aria-hidden="true" />
        </button>
        <span
          class="w-7 h-7 bg-linear-to-br from-indigo-500 to-violet-600 rounded-lg flex items-center justify-center text-white font-bold text-xs"
          aria-hidden="true"
          >KP</span
        >
        <span class="font-bold text-slate-800 dark:text-white">KeepPace</span>
      </div>
      <RouterView />
    </div>
  </div>

  <div v-else class="h-screen flex items-center justify-center bg-slate-100 dark:bg-slate-900">
    <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
  </div>

  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="drawerOpen && auth.isAuthenticated"
        class="lg:hidden fixed inset-0 z-40 flex"
        @keydown.esc="closeDrawer"
      >
        <div class="absolute inset-0 bg-black/40 backdrop-blur-xs" @click="closeDrawer"></div>
        <Sidebar drawer @navigate="closeDrawer" />
      </div>
    </Transition>
  </Teleport>

  <template v-if="auth.isAuthenticated">
    <CommandPalette v-model:open="ui.palette.value" :commands="commands" />
    <ShortcutsHelp v-model:open="ui.help.value" :commands="commands" />
  </template>

  <ToastContainer />
  <ConfirmDialog />
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu } from '@lucide/vue'
import Sidebar from './components/Sidebar.vue'
import ToastContainer from './components/ToastContainer.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import CommandPalette from './components/CommandPalette.vue'
import ShortcutsHelp from './components/ShortcutsHelp.vue'
import { buildCommands, ui } from './commands/index'
import { useDensity } from './composables/useDensity'
import { useShortcuts } from './composables/useShortcuts'
import { tasksApi } from './api/index'
import { useDarkMode } from './composables/useDarkMode'
import { useSidebar } from './composables/useSidebar'
import { useAuthStore } from './stores/auth'
import { useClientStore } from './stores/clientStore'
import { useTaskStore } from './stores/taskStore'

const { toggle: toggleDark } = useDarkMode()
const { toggle: toggleDensity } = useDensity()
const route = useRoute()
const router = useRouter()
const { open: drawerOpen, show: openDrawer, close: closeDrawer } = useSidebar()

// Le tiroir se referme dès qu'on change de page.
watch(() => route.fullPath, closeDrawer)
const auth = useAuthStore()
const clientStore = useClientStore()
const taskStore = useTaskStore()

const commands = computed(() =>
  buildCommands({
    router,
    toggleDark,
    toggleDensity,
    exportUrl: () => tasksApi.exportUrl(taskStore.queryParams()),
  }),
)

// Raccourcis : ceux des commandes (n, /, g t…) + Ctrl/⌘ K pour la palette.
useShortcuts(() => {
  if (!auth.isAuthenticated) return []
  return [
    { keys: ['k'], mod: true, run: () => (ui.palette.value = !ui.palette.value) },
    ...commands.value.filter((c) => c.hint).map((c) => ({ keys: c.hint!, run: c.run })),
  ]
})

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

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
</style>
