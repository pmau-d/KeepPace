<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/40 backdrop-blur-xs" @click="$emit('close')"></div>

      <!-- Modal -->
      <div
        class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md z-10 overflow-hidden"
        style="animation: modalIn 0.2s ease"
      >
        <!-- Modal header -->
        <div
          class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700"
        >
          <h2 class="text-lg font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <Copy class="w-5 h-5 text-indigo-500" aria-hidden="true" />
            {{ prefill ? 'Dupliquer la tâche' : 'Nouvelle tâche' }}
          </h2>
          <button
            class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 transition-colors"
            aria-label="Fermer"
            @click="$emit('close')"
          >
            <X class="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        <!-- Form -->
        <form class="px-6 py-5 space-y-4 max-h-[80vh] overflow-y-auto" @submit.prevent="submit">
          <!-- Title -->
          <div>
            <label
              for="new-task-field-1"
              class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >
              Titre <span class="text-red-500">*</span>
            </label>
            <input
              id="new-task-field-1"
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
            <label
              for="new-task-field-2"
              class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
              >Description</label
            >
            <textarea
              id="new-task-field-2"
              v-model="form.description"
              rows="2"
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 resize-none placeholder-slate-400"
              placeholder="Décrivez la tâche (optionnel)..."
            ></textarea>
          </div>

          <!-- Client autocomplete -->
          <div ref="clientDropdownRef" class="relative">
            <label
              for="new-task-field-3"
              class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >
              Client <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <input
                id="new-task-field-3"
                v-model="clientSearch"
                type="text"
                :class="[
                  'w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 placeholder-slate-400 transition',
                  form.client_id ? 'ring-2 ring-indigo-500' : 'focus:ring-2 focus:ring-indigo-500',
                ]"
                placeholder="Rechercher un client..."
                @input="onClientSearchInput"
                @focus="showClientDropdown = true"
                @blur="closeClientDropdown"
              />
              <Check
                v-if="form.client_id"
                class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-green-500"
                aria-label="Client sélectionné"
              />
            </div>

            <!-- Dropdown -->
            <div
              v-if="showClientDropdown"
              class="absolute z-20 w-full mt-1 bg-white dark:bg-slate-700 rounded-xl shadow-xl border border-slate-200 dark:border-slate-600 max-h-52 overflow-y-auto"
            >
              <div
                v-for="client in filteredClients"
                :key="client.id"
                class="px-3 py-2.5 text-sm hover:bg-indigo-50 dark:hover:bg-slate-600 cursor-pointer flex items-center gap-2"
                @mousedown.prevent="selectClient(client)"
              >
                <span
                  :class="[
                    'w-2 h-2 rounded-full shrink-0',
                    clientStore.presenceColor(client.presence_status),
                  ]"
                ></span>
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
                class="px-3 py-2.5 text-sm text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-slate-600 cursor-pointer border-t border-slate-200 dark:border-slate-600 font-medium flex items-center gap-2"
                @mousedown.prevent="openCreateClient"
              >
                <Plus class="w-4 h-4" aria-hidden="true" />
                Créer un nouveau client
              </div>
            </div>
          </div>

          <!-- Priority + Status -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label
                for="new-task-field-4"
                class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
                >Priorité</label
              >
              <BaseSelect id="new-task-field-4" v-model="form.priority" :options="PRIORITY_OPTIONS" block />
            </div>
            <div>
              <label
                for="new-task-field-5"
                class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
                >Statut</label
              >
              <BaseSelect
                id="new-task-field-5"
                v-model="form.status"
                :options="STATUS_OPTIONS.filter((o) => o.value !== 'DONE')"
                block
              />
            </div>
          </div>

          <!-- Due date -->
          <div>
            <label
              for="new-task-field-6"
              class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >
              Date d'échéance
            </label>
            <DatePicker id="new-task-field-6" v-model="form.due_date" placeholder="Sans échéance" />
          </div>

          <RecurrenceFields
            v-model:recurrence="form.recurrence"
            v-model:interval="form.recurrence_interval"
            id-prefix="new-task"
          />

          <!-- Error -->
          <p v-if="error" class="text-sm text-red-500 flex items-center gap-1">
            <CircleAlert class="w-4 h-4" aria-hidden="true" />
            {{ error }}
          </p>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="submitting || !form.client_id"
            class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm py-2.5 rounded-lg transition-colors shadow-xs"
          >
            {{ submitting ? 'Création en cours...' : prefill ? 'Dupliquer la tâche' : 'Créer la tâche' }}
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

<script setup lang="ts">
import { Check, CircleAlert, Copy, Plus, X } from '@lucide/vue'
import { ref, reactive, computed } from 'vue'
import { useClientStore } from '../stores/clientStore'
import { useTaskStore } from '../stores/taskStore'
import { useToastStore } from '../stores/toast'
import { errorMessage } from '../api/index'
import CreateClientModal from './CreateClientModal.vue'
import BaseSelect from './ui/BaseSelect.vue'
import DatePicker from './ui/DatePicker.vue'
import RecurrenceFields from './task/RecurrenceFields.vue'
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../utils/options'
import type {
  Client,
  Recurrence,
  TaskCreatePayload,
  TaskPriority,
  TaskStatus,
  TaskSummary,
} from '../types/api'

const props = withDefaults(defineProps<{ prefill?: TaskSummary | null }>(), { prefill: null })
const emit = defineEmits<{ close: [] }>()

const clientStore = useClientStore()
const taskStore = useTaskStore()
const toast = useToastStore()

const form = reactive<{
  title: string
  description: string
  client_id: string
  priority: TaskPriority
  status: TaskStatus
  due_date: string
  recurrence: Recurrence | ''
  recurrence_interval: number
}>({
  title: props.prefill ? `(Copie) ${props.prefill.title}` : '',
  description: props.prefill?.description ?? '',
  client_id: props.prefill?.client?.id ?? '',
  priority: props.prefill?.priority ?? 'MEDIUM',
  status: props.prefill?.status === 'DONE' ? 'TODO' : (props.prefill?.status ?? 'TODO'),
  due_date: props.prefill?.due_date ?? '',
  recurrence: props.prefill?.recurrence ?? '',
  recurrence_interval: props.prefill?.recurrence_interval ?? 1,
})

const clientSearch = ref(
  props.prefill?.client
    ? `${clientStore.fullName(props.prefill.client)} · ${props.prefill.client.company.name}`
    : '',
)
const showClientDropdown = ref(false)
const showCreateClientModal = ref(false)
const submitting = ref(false)
const error = ref('')

const filteredClients = computed(() => {
  if (!clientSearch.value) return clientStore.clients.slice(0, 8)
  const q = clientSearch.value.toLowerCase()
  return clientStore.clients
    .filter((c) => `${clientStore.fullName(c)} ${c.company.name}`.toLowerCase().includes(q))
    .slice(0, 8)
})

function selectClient(client: Client) {
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

function onClientCreated(client: Client) {
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
    const payload: TaskCreatePayload = {
      client_id: form.client_id,
      title: form.title,
      priority: form.priority,
      status: form.status,
    }
    if (form.due_date) payload.due_date = form.due_date
    if (form.description) payload.description = form.description
    if (form.recurrence) {
      payload.recurrence = form.recurrence
      payload.recurrence_interval = form.recurrence_interval
    }
    await taskStore.createTask(payload)
    toast.success(props.prefill ? 'Tâche dupliquée.' : 'Tâche créée.')
    emit('close')
  } catch (e) {
    error.value = errorMessage(e, 'Erreur lors de la création de la tâche. Veuillez réessayer.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
@keyframes modalIn {
  from {
    transform: scale(0.95) translateY(8px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}
</style>
