<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div @click="$emit('close')" class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>

      <div
        class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-sm z-10 overflow-hidden"
        style="animation: modalIn 0.2s ease"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <div>
            <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">Modifier le client</h2>
            <p class="text-xs text-slate-400 mt-0.5">{{ clientStore.fullName(client) }} · {{ client.company.name }}</p>
          </div>
          <button @click="$emit('close')" class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <form @submit.prevent="submit" class="px-6 py-5 space-y-4">
          <!-- Company section -->
          <div class="bg-slate-50 dark:bg-slate-700/40 rounded-xl p-3 space-y-2">
            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Entreprise</p>
            <div class="flex gap-2 items-center">
              <input
                v-model="companyName"
                type="text"
                required
                class="flex-1 text-sm bg-white dark:bg-slate-700 dark:text-slate-100 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Nom de l'entreprise"
              />
              <button
                type="button"
                @click="saveCompany"
                :disabled="savingCompany || companyName === client.company.name"
                class="text-xs px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-lg transition-colors whitespace-nowrap"
              >
                {{ savingCompany ? '…' : 'Renommer' }}
              </button>
            </div>
            <p v-if="companySaved" class="text-xs text-green-600 dark:text-green-400">✓ Entreprise renommée</p>
          </div>

          <!-- First + Last name -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Prénom <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.first_name"
                required
                type="text"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Nom <span class="text-slate-400 font-normal text-xs">(optionnel)</span>
              </label>
              <input
                v-model="form.last_name"
                type="text"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Email</label>
            <input
              v-model="form.email"
              type="email"
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 placeholder-slate-400"
              placeholder="email@exemple.com"
            />
          </div>

          <!-- Absence end date -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Absent jusqu'au
              <span class="text-slate-400 font-normal text-xs">(optionnel)</span>
            </label>
            <input
              v-model="form.absence_end_date"
              type="date"
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            />
            <button
              v-if="form.absence_end_date"
              type="button"
              @click="form.absence_end_date = ''"
              class="mt-1 text-xs text-slate-400 hover:text-red-500 transition-colors"
            >
              ✕ Supprimer l'absence
            </button>
          </div>

          <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

          <button
            type="submit"
            :disabled="submitting"
            class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors"
          >
            {{ submitting ? 'Enregistrement…' : 'Enregistrer les modifications' }}
          </button>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useClientStore } from '../stores/clientStore.js'

const props = defineProps({ client: Object })
const emit = defineEmits(['close', 'updated'])

const clientStore = useClientStore()

const form = reactive({
  first_name: props.client.first_name,
  last_name: props.client.last_name ?? '',
  email: props.client.email ?? '',
  absence_end_date: props.client.absence_end_date ?? '',
})

const companyName = ref(props.client.company.name)
const savingCompany = ref(false)
const companySaved = ref(false)
const submitting = ref(false)
const error = ref('')

async function saveCompany() {
  if (!companyName.value.trim() || companyName.value === props.client.company.name) return
  savingCompany.value = true
  try {
    await clientStore.editCompany(props.client.company_id, companyName.value.trim())
    companySaved.value = true
    setTimeout(() => { companySaved.value = false }, 2000)
  } catch {
    companyName.value = props.client.company.name
    error.value = "Ce nom d'entreprise existe déjà."
  } finally {
    savingCompany.value = false
  }
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const payload = { first_name: form.first_name }
    if (form.last_name) payload.last_name = form.last_name
    if (form.email) payload.email = form.email
    payload.absence_end_date = form.absence_end_date || null
    const updated = await clientStore.updateClient(props.client.id, payload)
    emit('updated', updated)
  } catch {
    error.value = 'Erreur lors de la modification. Veuillez réessayer.'
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

