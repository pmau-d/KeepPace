<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex">
      <!-- Backdrop -->
      <div class="flex-1 bg-black/30 backdrop-blur-xs" @click="$emit('close')"></div>

      <!-- Panel -->
      <div
        class="w-full max-w-lg bg-white dark:bg-slate-800 shadow-2xl flex flex-col h-full border-l border-slate-200 dark:border-slate-700"
        style="animation: slideIn 0.25s ease"
      >
        <!-- Header -->
        <div
          class="flex items-start justify-between p-5 border-b border-slate-200 dark:border-slate-700 shrink-0"
        >
          <div class="flex-1 min-w-0 pr-3">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <StatusBadge :status="task.status" />
              <PriorityBadge :priority="task.priority" />
            </div>
            <h2 class="font-bold text-lg text-slate-800 dark:text-slate-100 leading-snug">
              {{ task.title }}
            </h2>
            <p class="text-sm text-slate-400 mt-0.5 flex items-center gap-1.5">
              <span
                :class="[
                  'w-2 h-2 rounded-full shrink-0',
                  clientStore.presenceColor(task.client.presence_status),
                ]"
              ></span>
              {{ clientStore.fullName(task.client) }} · {{ task.client.company.name }}
            </p>
            <!-- Sub-status inline -->
            <div
              v-if="task.sub_status"
              class="mt-1.5 inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 font-medium"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                />
              </svg>
              {{ task.sub_status }}
            </div>
          </div>
          <button
            class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 shrink-0"
            @click="$emit('close')"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-slate-200 dark:border-slate-700 shrink-0">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="[
              'flex-1 py-2.5 text-sm font-medium transition-colors flex items-center justify-center gap-1.5',
              activeTab === tab.id
                ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-500'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200',
            ]"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
            <span
              v-if="tab.id === 'comments' && task.comments?.length"
              class="text-xs px-1.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 font-semibold"
            >
              {{ task.comments.length }}
            </span>
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto">
          <!-- ═══ TAB: EDIT ═══ -->
          <div v-if="activeTab === 'edit'" class="p-5 space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <!-- Status -->
              <div>
                <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1"
                  >Statut</label
                >
                <select
                  v-model="form.status"
                  class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="TODO">À faire</option>
                  <option value="IN_PROGRESS">En cours</option>
                  <option value="BLOCKED">En attente Client</option>
                  <option value="DONE">Terminé</option>
                </select>
              </div>
              <!-- Priority -->
              <div>
                <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1"
                  >Priorité</label
                >
                <select
                  v-model="form.priority"
                  class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="LOW">🟢 Basse</option>
                  <option value="MEDIUM">🟡 Moyenne</option>
                  <option value="HIGH">🔴 Haute</option>
                </select>
              </div>
            </div>

            <!-- Sub-status -->
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                Statut personnalisé
                <span class="font-normal text-slate-400"
                  >(optionnel — ex : En attente vendor, Validation DG…)</span
                >
              </label>
              <div class="relative">
                <input
                  v-model="form.sub_status"
                  type="text"
                  list="sub-status-suggestions"
                  class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg pl-8 pr-3 py-2 focus:ring-2 focus:ring-violet-500 placeholder-slate-400"
                  placeholder="Ex: En attente vendor, En attente customer…"
                />
                <svg
                  class="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-violet-400 pointer-events-none"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                  />
                </svg>
              </div>
              <datalist id="sub-status-suggestions">
                <option value="En attente customer" />
                <option value="En attente vendor" />
                <option value="En attente validation DG" />
                <option value="En attente retour DSI" />
                <option value="En attente chiffrage" />
                <option value="En attente livraison" />
                <option value="En cours de review" />
                <option value="Bloqué — dépendance externe" />
              </datalist>
              <!-- Quick tags -->
              <div class="flex flex-wrap gap-1.5 mt-2">
                <button
                  v-for="s in quickSubStatuses"
                  :key="s"
                  :class="[
                    'text-xs px-2 py-0.5 rounded-full border transition-colors',
                    form.sub_status === s
                      ? 'bg-violet-100 dark:bg-violet-900/40 border-violet-400 text-violet-700 dark:text-violet-300'
                      : 'border-slate-200 dark:border-slate-600 text-slate-500 dark:text-slate-400 hover:border-violet-400 hover:text-violet-600',
                  ]"
                  @click="form.sub_status = form.sub_status === s ? '' : s"
                >
                  {{ s }}
                </button>
              </div>
            </div>

            <!-- Due date -->
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1"
                >Date d'échéance</label
              >
              <input
                v-model="form.due_date"
                type="date"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1"
                >Description</label
              >
              <textarea
                v-model="form.description"
                rows="3"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 resize-none"
                placeholder="Description…"
              ></textarea>
            </div>

            <!-- Log comment -->
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1"
                >Note de modification (audit log)</label
              >
              <input
                v-model="form.comment"
                type="text"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
                placeholder="Raison de la modification…"
              />
            </div>

            <button
              :disabled="saving"
              class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-sm py-2.5 rounded-lg transition-colors"
              @click="saveChanges"
            >
              {{ saving ? 'Enregistrement…' : 'Sauvegarder' }}
            </button>

            <!-- ─── Dupliquer ───────────────────────────────────────────── -->
            <div class="pt-1 border-t border-slate-200 dark:border-slate-700">
              <button
                class="w-full flex items-center justify-center gap-2 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-900/20 dark:hover:bg-indigo-900/40 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 font-medium text-sm py-2 rounded-lg transition-colors"
                @click="$emit('duplicate', task)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                Dupliquer la tâche
              </button>
              <p class="text-xs text-slate-400 text-center mt-1">
                Crée une nouvelle tâche pré-remplie avec les mêmes informations.
              </p>
            </div>

            <!-- ─── Fermer / Réouvrir ───────────────────────────────────── -->
            <div class="pt-1 border-t border-slate-200 dark:border-slate-700 space-y-2">
              <!-- Fermer la tâche (→ DONE, réversible) -->
              <button
                v-if="task.status !== 'DONE'"
                :disabled="closing"
                class="w-full flex items-center justify-center gap-2 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-900/20 dark:hover:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 font-medium text-sm py-2 rounded-lg transition-colors disabled:opacity-50"
                @click="handleClose"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {{ closing ? '…' : 'Fermer la tâche' }}
              </button>

              <!-- Réouvrir (→ TODO, quand DONE) -->
              <button
                v-if="task.status === 'DONE'"
                :disabled="reopening"
                class="w-full flex items-center justify-center gap-2 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/40 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800 font-medium text-sm py-2 rounded-lg transition-colors disabled:opacity-50"
                @click="handleReopen"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                {{ reopening ? '…' : 'Réouvrir la tâche' }}
              </button>

              <p class="text-xs text-slate-400 text-center">
                <span v-if="task.status !== 'DONE'"
                  >Fermer conserve la tâche dans l'historique. Elle peut être réouverte.</span
                >
                <span v-else class="text-blue-500 dark:text-blue-400"
                  >Cette tâche est fermée — réouvrez-la pour la remettre en cours.</span
                >
              </p>
            </div>

            <!-- ─── Supprimer définitivement ───────────────────────────── -->
            <div class="pt-1 border-t border-slate-200 dark:border-slate-700">
              <button
                class="w-full border border-red-300 dark:border-red-800 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 font-medium text-sm py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
                @click="confirmDelete"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                Supprimer définitivement
              </button>
              <p class="text-xs text-red-400 text-center mt-1">
                Irréversible — supprime la tâche et tout son historique.
              </p>
            </div>
          </div>

          <!-- ═══ TAB: COMMENTS ═══ -->
          <div v-if="activeTab === 'comments'" class="flex flex-col h-full">
            <!-- Comment list -->
            <div class="flex-1 overflow-y-auto p-5 space-y-3">
              <div v-if="!task.comments?.length" class="text-slate-400 text-sm py-8 text-center">
                <svg
                  class="w-10 h-10 mx-auto mb-2 opacity-40"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
                <p>Aucun commentaire pour l'instant.</p>
              </div>
              <div v-for="c in task.comments" :key="c.id" class="group flex gap-3">
                <div
                  class="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center shrink-0 mt-0.5"
                >
                  <svg
                    class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"
                    />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="bg-slate-50 dark:bg-slate-700/50 rounded-xl px-3 py-2">
                    <p class="text-sm text-slate-700 dark:text-slate-200 whitespace-pre-wrap wrap-break-word">
                      {{ c.content }}
                    </p>
                  </div>
                  <div class="flex items-center justify-between mt-1 px-1">
                    <p class="text-xs text-slate-400">{{ formatDateTime(c.created_at) }}</p>
                    <button
                      class="opacity-0 group-hover:opacity-100 text-xs text-red-400 hover:text-red-600 transition-all"
                      @click="removeComment(c.id)"
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- New comment input -->
            <div class="p-4 border-t border-slate-200 dark:border-slate-700">
              <div class="flex gap-2">
                <textarea
                  v-model="newComment"
                  rows="2"
                  class="flex-1 text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 resize-none placeholder-slate-400"
                  placeholder="Écrire un commentaire… (Ctrl+Entrée pour envoyer)"
                  @keydown.ctrl.enter="submitComment"
                  @keydown.meta.enter="submitComment"
                ></textarea>
                <button
                  :disabled="!newComment.trim() || postingComment"
                  class="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-xl transition-colors shrink-0"
                  @click="submitComment"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                    />
                  </svg>
                </button>
              </div>
              <p class="text-xs text-slate-400 mt-1">Ctrl+Entrée pour envoyer</p>
            </div>
          </div>

          <!-- ═══ TAB: HISTORY ═══ -->
          <div v-if="activeTab === 'history'" class="p-5">
            <div v-if="logsLoading" class="text-slate-400 text-sm animate-pulse">Chargement…</div>
            <div v-else-if="!logs.length" class="text-slate-400 text-sm py-8 text-center">
              Aucun historique.
            </div>
            <div v-else class="relative pl-5">
              <div class="absolute left-[9px] top-1 bottom-1 w-px bg-slate-200 dark:bg-slate-700"></div>
              <div v-for="log in logs" :key="log.id" class="relative mb-4 last:mb-0">
                <div
                  class="absolute -left-5 top-2 w-3 h-3 rounded-full bg-indigo-500 border-2 border-white dark:border-slate-800 shadow-sm"
                ></div>
                <div class="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-3">
                  <p class="text-xs text-slate-400 mb-1.5">{{ formatDateTime(log.created_at) }}</p>
                  <p class="text-sm text-slate-700 dark:text-slate-200 leading-snug">
                    <span class="font-semibold">{{ fieldLabel(log.field_changed) }}</span>
                    <span v-if="log.old_value" class="text-slate-400 line-through mx-1">{{
                      formatValue(log.field_changed, log.old_value)
                    }}</span>
                    <span v-if="log.old_value && log.new_value" class="text-slate-400">→</span>
                    <span
                      v-if="log.new_value"
                      class="text-indigo-600 dark:text-indigo-400 font-medium ml-1"
                      >{{ formatValue(log.field_changed, log.new_value) }}</span
                    >
                  </p>
                  <p v-if="log.comment" class="text-xs text-slate-500 mt-1.5 italic">💬 {{ log.comment }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useTaskStore } from '../stores/taskStore.js'
import { useClientStore } from '../stores/clientStore.js'
import { tasksApi } from '../api/index.js'
import StatusBadge from './StatusBadge.vue'
import PriorityBadge from './PriorityBadge.vue'

defineEmits(['close', 'duplicate'])

const taskStore = useTaskStore()
const clientStore = useClientStore()
const task = taskStore.selectedTask

const activeTab = ref('edit')
const tabs = [
  { id: 'edit', label: '✏️ Modifier' },
  { id: 'comments', label: '💬 Commentaires' },
  { id: 'history', label: '📋 Historique' },
]

const quickSubStatuses = [
  'En attente customer',
  'En attente vendor',
  'Validation DG',
  'Retour DSI',
  'En cours de review',
]

const form = reactive({
  status: task.status,
  priority: task.priority,
  sub_status: task.sub_status ?? '',
  due_date: task.due_date ?? '',
  description: task.description ?? '',
  comment: '',
})

const saving = ref(false)
const closing = ref(false)
const reopening = ref(false)
const logs = ref([])
const logsLoading = ref(false)
const newComment = ref('')
const postingComment = ref(false)

async function loadLogs() {
  logsLoading.value = true
  try {
    const res = await tasksApi.getLogs(task.id)
    logs.value = [...res.data].reverse()
  } finally {
    logsLoading.value = false
  }
}

async function saveChanges() {
  saving.value = true
  try {
    const payload = { ...form }
    if (!payload.due_date) payload.due_date = null
    if (!payload.description) payload.description = null
    if (!payload.sub_status) payload.sub_status = null
    if (!payload.comment) delete payload.comment
    await taskStore.updateTask(task.id, payload)
    form.comment = ''
    await loadLogs()
  } finally {
    saving.value = false
  }
}

async function submitComment() {
  if (!newComment.value.trim() || postingComment.value) return
  postingComment.value = true
  try {
    const res = await tasksApi.addComment(task.id, newComment.value.trim())
    // Push directly to task.comments (reactive)
    if (!task.comments) task.comments = []
    task.comments.push(res.data)
    newComment.value = ''
  } finally {
    postingComment.value = false
  }
}

async function removeComment(commentId) {
  if (!window.confirm('Supprimer ce commentaire ?')) return
  await tasksApi.deleteComment(task.id, commentId)
  const idx = task.comments.findIndex((c) => c.id === commentId)
  if (idx !== -1) task.comments.splice(idx, 1)
}

async function handleClose() {
  closing.value = true
  try {
    await taskStore.closeTask(task.id)
    await loadLogs()
  } finally {
    closing.value = false
  }
}

async function handleReopen() {
  reopening.value = true
  try {
    await taskStore.reopenTask(task.id)
    form.status = 'TODO'
    await loadLogs()
  } finally {
    reopening.value = false
  }
}

async function confirmDelete() {
  if (
    !window.confirm(
      `Supprimer définitivement la tâche "${task.title}" ?\n\nCette action est irréversible — la tâche et tout son historique seront perdus.`,
    )
  )
    return
  await taskStore.deleteTask(task.id)
}

// ─── Formatting ──────────────────────────────────────────────────────────────
const STATUS_LABELS = {
  TODO: 'À faire',
  IN_PROGRESS: 'En cours',
  BLOCKED: 'En attente Client',
  DONE: 'Terminé',
}
const PRIORITY_LABELS = { LOW: 'Basse', MEDIUM: 'Moyenne', HIGH: 'Haute' }
const FIELD_LABELS = {
  status: 'Statut',
  sub_status: 'Statut personnalisé',
  due_date: "Date d'échéance",
  description: 'Description',
  priority: 'Priorité',
  title: 'Titre',
  client_id: 'Client',
}

function fieldLabel(f) {
  return FIELD_LABELS[f] ?? f
}
function formatValue(field, value) {
  if (field === 'status') return STATUS_LABELS[value] ?? value
  if (field === 'priority') return PRIORITY_LABELS[value] ?? value
  if (field === 'due_date' && value)
    return new Date(value).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
  return value
}
function formatDateTime(dt) {
  return new Date(dt).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(loadLogs)
</script>

<style scoped>
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
