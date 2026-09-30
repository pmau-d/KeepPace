<template>
  <div class="fixed inset-0 z-60 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/50 backdrop-blur-xs" @click="$emit('close')"></div>

    <!-- Modal -->
    <div
      class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-sm z-10 overflow-hidden"
      style="animation: modalIn 0.2s ease"
    >
      <!-- Header -->
      <div
        class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700"
      >
        <div>
          <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">Nouveau client</h2>
          <p class="text-xs text-slate-400 mt-0.5">Créez un client et son entreprise</p>
        </div>
        <button
          class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 transition-colors"
          aria-label="Fermer"
          @click="$emit('close')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form class="px-6 py-5 space-y-4" @submit.prevent="submit">
        <!-- Company autocomplete -->
        <div class="relative">
          <label
            for="new-client-field-1"
            class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
          >
            Entreprise <span class="text-red-500">*</span>
          </label>
          <input
            id="new-client-field-1"
            v-model="companySearch"
            type="text"
            required
            :class="[
              'w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 placeholder-slate-400 transition',
              form.company_id ? 'ring-2 ring-indigo-500' : 'focus:ring-2 focus:ring-indigo-500',
            ]"
            placeholder="Nom de l'entreprise"
            @input="onCompanyInput"
            @focus="showCompanyDropdown = true"
            @blur="closeCompanyDropdown"
          />

          <div
            v-if="showCompanyDropdown && companySearch"
            class="absolute z-10 w-full mt-1 bg-white dark:bg-slate-700 rounded-xl shadow-lg border border-slate-200 dark:border-slate-600 max-h-40 overflow-y-auto"
          >
            <div
              v-for="company in filteredCompanies"
              :key="company.id"
              class="px-3 py-2 text-sm text-slate-800 dark:text-slate-100 hover:bg-indigo-50 dark:hover:bg-slate-600 cursor-pointer"
              @mousedown.prevent="selectCompany(company)"
            >
              {{ company.name }}
            </div>
            <div
              v-if="!form.company_id"
              class="px-3 py-2 text-sm text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-slate-600 cursor-pointer border-t border-slate-200 dark:border-slate-600 font-medium flex items-center gap-1.5"
              @mousedown.prevent="createAndSelectCompany"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Créer "{{ companySearch }}"
            </div>
          </div>
        </div>

        <!-- First + Last name -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label
              for="new-client-field-2"
              class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >
              Prénom <span class="text-red-500">*</span>
            </label>
            <input
              id="new-client-field-2"
              v-model="form.first_name"
              required
              type="text"
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label
              for="new-client-field-3"
              class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >
              Nom
              <span class="text-slate-400 font-normal text-xs">(optionnel)</span>
            </label>
            <input
              id="new-client-field-3"
              v-model="form.last_name"
              type="text"
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <!-- Email -->
        <div>
          <label
            for="new-client-field-4"
            class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >Email</label
          >
          <input
            id="new-client-field-4"
            v-model="form.email"
            type="email"
            class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 placeholder-slate-400"
            placeholder="contact@example.com"
          />
        </div>

        <AbsencePeriodFields
          v-model:start="form.absence_start_date"
          v-model:end="form.absence_end_date"
          id-prefix="new-client-absence"
        />

        <!-- Error -->
        <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="submitting || !form.company_id"
          class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm py-2.5 rounded-lg transition-colors"
        >
          {{ submitting ? 'Création...' : 'Créer le client' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { errorMessage, httpStatus } from '../api/index'
import { useClientStore } from '../stores/clientStore'
import AbsencePeriodFields from './AbsencePeriodFields.vue'
import type { Client, ClientPayload, Company } from '../types/api'

const emit = defineEmits<{ close: []; created: [client: Client] }>()
const clientStore = useClientStore()
const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  absence_start_date: '',
  absence_end_date: '',
  company_id: '',
})

const companySearch = ref('')
const showCompanyDropdown = ref(false)
const submitting = ref(false)
const error = ref('')

const filteredCompanies = computed(() => {
  const q = companySearch.value.toLowerCase()
  return clientStore.companies.filter((c) => c.name.toLowerCase().includes(q)).slice(0, 6)
})

function selectCompany(company: Company) {
  form.company_id = company.id
  companySearch.value = company.name
  showCompanyDropdown.value = false
}

function onCompanyInput() {
  form.company_id = ''
  showCompanyDropdown.value = true
}

function closeCompanyDropdown() {
  setTimeout(() => {
    showCompanyDropdown.value = false
  }, 150)
}

async function createAndSelectCompany() {
  if (!companySearch.value.trim()) return
  // Si la company existe déjà localement, la sélectionner directement
  const existing = clientStore.companies.find(
    (c) => c.name.toLowerCase() === companySearch.value.trim().toLowerCase(),
  )
  if (existing) {
    selectCompany(existing)
    return
  }
  try {
    const comp = await clientStore.createCompany(companySearch.value.trim())
    selectCompany(comp)
  } catch (e) {
    // Conflit 400 : quelqu'un l'a créée entre-temps — recharger et sélectionner
    if (httpStatus(e) === 400) {
      await clientStore.fetchCompanies()
      const fresh = clientStore.companies.find(
        (c) => c.name.toLowerCase() === companySearch.value.trim().toLowerCase(),
      )
      if (fresh) selectCompany(fresh)
    }
  }
}

async function submit() {
  if (!form.company_id) {
    error.value = 'Veuillez sélectionner ou créer une entreprise.'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const payload: ClientPayload = {
      company_id: form.company_id,
      first_name: form.first_name,
    }
    if (form.last_name) payload.last_name = form.last_name
    if (form.email) payload.email = form.email
    if (form.absence_start_date) payload.absence_start_date = form.absence_start_date
    if (form.absence_end_date) payload.absence_end_date = form.absence_end_date
    const client = await clientStore.createClient(payload)
    emit('created', client)
  } catch (e) {
    error.value = errorMessage(e, 'Erreur lors de la création du client. Veuillez réessayer.')
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
