<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[75] flex items-start justify-center p-4 pt-[12vh]"
      role="dialog"
      aria-modal="true"
      aria-label="Palette de commandes"
      @keydown.esc.prevent="close"
    >
      <div class="absolute inset-0 bg-black/40 backdrop-blur-xs" @click="close"></div>
      <div
        class="relative w-full max-w-xl bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden"
      >
        <div class="flex items-center gap-3 px-4 border-b border-slate-200 dark:border-slate-700">
          <Search class="w-4 h-4 text-slate-400 shrink-0" aria-hidden="true" />
          <input
            ref="input"
            v-model="query"
            type="text"
            role="combobox"
            aria-expanded="true"
            aria-controls="palette-results"
            :aria-activedescendant="items[active] ? `palette-item-${active}` : undefined"
            aria-label="Rechercher une commande, une tâche ou un client"
            placeholder="Commande, tâche ou client…"
            class="flex-1 py-3.5 text-sm bg-transparent border-0 focus:ring-0 focus:outline-none text-slate-800 dark:text-slate-100 placeholder-slate-400"
            @keydown.down.prevent="move(1)"
            @keydown.up.prevent="move(-1)"
            @keydown.enter.prevent="choose(items[active])"
          />
          <kbd
            class="text-[10px] text-slate-400 border border-slate-200 dark:border-slate-600 rounded-sm px-1.5 py-0.5"
            >Échap</kbd
          >
        </div>

        <ul
          id="palette-results"
          role="listbox"
          class="max-h-[50vh] overflow-y-auto py-2"
          aria-label="Résultats"
        >
          <template v-for="(item, index) in items" :key="item.key">
            <li
              v-if="index === 0 || items[index - 1]!.group !== item.group"
              role="presentation"
              class="px-4 pt-2 pb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400"
            >
              {{ item.group }}
            </li>
            <li
              :id="`palette-item-${index}`"
              role="option"
              :aria-selected="index === active"
              :class="[
                'mx-2 px-3 py-2 rounded-lg flex items-center gap-3 text-sm cursor-pointer',
                index === active
                  ? 'bg-indigo-50 dark:bg-slate-700 text-indigo-700 dark:text-indigo-200'
                  : 'text-slate-700 dark:text-slate-200',
              ]"
              @mousemove="active = index"
              @click="choose(item)"
            >
              <component :is="item.icon" class="w-4 h-4 shrink-0 opacity-70" aria-hidden="true" />
              <span
                v-if="item.dot"
                :class="['w-2 h-2 rounded-full shrink-0', item.dot]"
                aria-hidden="true"
              ></span>
              <span class="flex-1 truncate">{{ item.label }}</span>
              <span v-if="item.detail" class="text-xs text-slate-400 truncate max-w-48">{{
                item.detail
              }}</span>
              <span v-if="item.hint" class="flex gap-1">
                <kbd
                  v-for="key in item.hint"
                  :key="key"
                  class="text-[10px] min-w-5 text-center text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-600 rounded-sm px-1 py-0.5"
                  >{{ key }}</kbd
                >
              </span>
            </li>
          </template>
          <li v-if="!items.length" class="px-4 py-6 text-sm text-center text-slate-400">
            {{ searching ? 'Recherche…' : 'Aucun résultat' }}
          </li>
        </ul>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { FileText, Search, User } from '@lucide/vue'
import { tasksApi } from '../api/index'
import type { Command } from '../commands/index'
import { useClientStore } from '../stores/clientStore'
import { useTaskStore } from '../stores/taskStore'
import { fullName, presenceColor } from '../utils/labels'
import { normalize } from '../utils/text'
import type { TaskSummary } from '../types/api'

const props = defineProps<{ commands: Command[] }>()
const open = defineModel<boolean>('open', { required: true })

interface Item {
  key: string
  group: string
  label: string
  detail?: string
  icon: Component
  dot?: string
  hint?: string[]
  run: () => void
}

const router = useRouter()
const clientStore = useClientStore()
const taskStore = useTaskStore()
const input = ref<HTMLInputElement | null>(null)
const query = ref('')
const active = ref(0)
const tasks = ref<TaskSummary[]>([])
const searching = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | undefined
let searchId = 0

const matches = (text: string) => normalize(text).includes(normalize(query.value))

const items = computed<Item[]>(() => {
  const q = query.value.trim()
  const commands = props.commands
    .filter((c) => !q || matches(`${c.label} ${c.keywords ?? ''}`))
    .map((c) => ({ key: c.id, group: c.group, label: c.label, icon: c.icon, hint: c.hint, run: c.run }))
  if (!q) return commands
  const clients = clientStore.clients
    .filter((c) => matches(`${fullName(c)} ${c.company.name}`))
    .slice(0, 5)
    .map<Item>((c) => ({
      key: `client-${c.id}`,
      group: 'Clients',
      label: fullName(c),
      detail: c.company.name,
      icon: User,
      dot: presenceColor(c.presence_status),
      run: async () => {
        await router.push({ name: 'tasks' })
        taskStore.filters.clientId = null
        await taskStore.setClientFilter(c.id)
      },
    }))
  const found = tasks.value.map<Item>((t) => ({
    key: `task-${t.id}`,
    group: 'Tâches',
    label: t.title,
    detail: `${fullName(t.client)} · ${t.client.company.name}`,
    icon: FileText,
    run: () => void router.push({ name: 'task', params: { id: t.id } }),
  }))
  return [...found, ...clients, ...commands]
})

function move(step: number) {
  const count = items.value.length
  if (count) active.value = (active.value + step + count) % count
}

function close() {
  open.value = false
}

function choose(item: Item | undefined) {
  if (!item) return
  close()
  item.run()
}

watch(query, (value) => {
  active.value = 0
  clearTimeout(searchTimer)
  const q = value.trim()
  if (q.length < 2) {
    tasks.value = []
    return
  }
  searching.value = true
  const current = ++searchId
  searchTimer = setTimeout(async () => {
    try {
      const { data } = await tasksApi.list({ search: q, limit: 6, offset: 0 })
      if (current === searchId) tasks.value = data.items
    } finally {
      if (current === searchId) searching.value = false
    }
  }, 200)
})

watch(open, async (value) => {
  if (!value) return
  query.value = ''
  tasks.value = []
  active.value = 0
  await nextTick()
  input.value?.focus()
})
</script>
