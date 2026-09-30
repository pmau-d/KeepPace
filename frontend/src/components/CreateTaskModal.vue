<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div @click="$emit('close')" class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>

      <!-- Modal -->
      <div
        class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md z-10 overflow-hidden"
        style="animation: modalIn 0.2s ease"
      >
        <!-- Modal header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <svg v-if="prefill" class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
            </svg>
            {{ prefill ? 'Dupliquer la tâche' : 'Nouvelle tâche' }}
          </h2>
          <button
            @click="$emit('close')"
            class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="submit" class="px-6 py-5 space-y-4 max-h-[80vh] overflow-y-auto">
          <!-- Title -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Titre <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.title"
              required
              type="text"
              autofocus
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 placeholder-slate-400"
              placeholder="Titre de la tâche"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
            <textarea
              v-model="form.description"
              rows="2"
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 resize-none placeholder-slate-400"
              placeholder="Décrivez la tâche (optionnel)..."
            ></textarea>
          </div>

          <!-- Client autocomplete -->
          <div class="relative" ref="clientDropdownRef">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Client <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <input
                v-model="clientSearch"
                @input="onClientSearchInput"
                @focus="showClientDropdown = true"
                @blur="closeClientDropdown"
                type="text"
                :class="[
                  'w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 placeholder-slate-400 transition',
                  form.client_id
                    ? 'ring-2 ring-indigo-500'
                    : 'focus:ring-2 focus:ring-indigo-500',
                ]"
                placeholder="Rechercher un client..."
              />
              <span
                v-if="form.client_id"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-green-500"
              >✓</span>
            </div>

            <!-- Dropdown -->
            <div
              v-if="showClientDropdown"
              class="absolute z-20 w-full mt-1 bg-white dark:bg-slate-700 rounded-xl shadow-xl border border-slate-200 dark:border-slate-600 max-h-52 overflow-y-auto"
            >
              <div
                v-for="client in filteredClients"
                :key="client.id"
                @mousedown.prevent="selectClient(client)"
                class="px-3 py-2.5 text-sm hover:bg-indigo-50 dark:hover:bg-slate-600 cursor-pointer flex items-center gap-2"
              >
                <span :class="['w-2 h-2 rounded-full flex-shrink-0', clientStore.presenceColor(client.presence_status)]"></span>
                <span class="font-medium text-slate-800 dark:text-slate-100">
                  {{ clientStore.fullName(client) }}
                </span>
                <span class="text-slate-400 text-xs">· {{ client.company.name }}</span>
              </div>

              <div
                v-if="filteredClients.length === 0 && clientSearch"
                class="px-3 py-2 text-sm text-slate-400"
              >
                Aucun résultat pour "{{ clientSearch }}"
              </div>

              <div
                @mousedown.prevent="openCreateClient"
                class="px-3 py-2.5 text-sm text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-slate-600 cursor-pointer border-t border-slate-200 dark:border-slate-600 font-medium flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Créer un nouveau client
              </div>
            </div>
          </div>

          <!-- Priority + Status -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Priorité</label>
              <select
                v-model="form.priority"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              >
                <option value="LOW">🟢 Basse</option>
                <option value="MEDIUM">🟡 Moyenne</option>
                <option value="HIGH">🔴 Haute</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Statut</label>
              <select
                v-model="form.status"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              >
                <option value="TODO">À faire</option>
                <option value="IN_PROGRESS">En cours</option>
                <option value="BLOCKED">En attente</option>
              </select>
            </div>
          </div>

          <!-- Due date -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Date d'échéance
            </label>
            <input
              v-model="form.due_date"
              type="date"
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <!-- Error -->
          <p v-if="error" class="text-sm text-red-500 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ error }}
          </p>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="submitting || !form.client_id"
            class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm py-2.5 rounded-lg transition-colors shadow-sm"
          >
            {{ submitting ? 'Création en cours...' : (prefill ? 'Dupliquer la tâche' : 'Créer la tâche') }}
          </button>
        </form>
      </div>

      <!-- Sub-modal: create client -->
      <CreateClientModal
        v-if="showCreateClientModal"
        @close="showCreateClientModal = false"
        @created="onClientCreated"
      />
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useClientStore } from '../stores/clientStore.js'
import { useTaskStore } from '../stores/taskStore.js'
import CreateClientModal from './CreateClientModal.vue'

const props = defineProps({ prefill: { type: Object, default: null } })
const emit = defineEmits(['close'])

const clientStore = useClientStore()
const taskStore = useTaskStore()

const form = reactive({
  title: props.prefill ? `(Copie) ${props.prefill.title}` : '',
  description: props.prefill?.description ?? '',
  client_id: props.prefill?.client?.id ?? '',
  priority: props.prefill?.priority ?? 'MEDIUM',
  status: props.prefill?.status === 'DONE' ? 'TODO' : (props.prefill?.status ?? 'TODO'),
  due_date: props.prefill?.due_date ?? '',
})

const clientSearch = ref(
  props.prefill?.client
    ? `${clientStore.fullName(props.prefill.client)} · ${props.prefill.client.company.name}`
    : ''
)
const showClientDropdown = ref(false)
const showCreateClientModal = ref(false)
const submitting = ref(false)
const error = ref('')

const filteredClients = computed(() => {
  if (!clientSearch.value) return clientStore.clients.slice(0, 8)
  const q = clientSearch.value.toLowerCase()
  return clientStore.clients
    .filter((c) =>
      `${clientStore.fullName(c)} ${c.company.name}`.toLowerCase().includes(q),
    )
    .slice(0, 8)
})

function selectClient(client) {
  form.client_id = client.id
  clientSearch.value = `${clientStore.fullName(client)} · ${client.company.name}`
  showClientDropdown.value = false
}

function onClientSearchInput() {
  form.client_id = ''
  showClientDropdown.value = true
}

function closeClientDropdown() {
  setTimeout(() => {
    showClientDropdown.value = false
  }, 150)
}

function openCreateClient() {
  showClientDropdown.value = false
  showCreateClientModal.value = true
}

function onClientCreated(client) {
  showCreateClientModal.value = false
  selectClient(client)
}

async function submit() {
  if (!form.client_id) {
    error.value = 'Veuillez sélectionner un client.'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const payload = { ...form }
    if (!payload.due_date) delete payload.due_date
    if (!payload.description) delete payload.description
    await taskStore.createTask(payload)
    emit('close')
  } catch {
    error.value = 'Erreur lors de la création de la tâche. Veuillez réessayer.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
@keyframes modalIn {
  from { transform: scale(0.95) translateY(8px); opacity: 0; }
  to   { transform: scale(1) translateY(0);      opacity: 1; }
}
</style>



