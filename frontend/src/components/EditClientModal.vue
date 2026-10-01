<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-60 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50 backdrop-blur-xs" @click="$emit('close')"></div>

      <div
        class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-sm z-10 overflow-hidden"
        style="animation: modalIn 0.2s ease"
      >
        <!-- Header -->
        <div
          class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700"
        >
          <div>
            <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">Modifier le client</h2>
            <p class="text-xs text-slate-400 mt-0.5">
              {{ clientStore.fullName(client) }} · {{ client.company.name }}
            </p>
          </div>
          <button
            class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400"
            aria-label="Fermer"
            @click="$emit('close')"
          >
            <X class="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        <form class="px-6 py-5 space-y-4" @submit.prevent="submit">
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
                :disabled="savingCompany || companyName === client.company.name"
                class="text-xs px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-lg transition-colors whitespace-nowrap"
                @click="saveCompany"
              >
                {{ savingCompany ? '…' : 'Renommer' }}
              </button>
            </div>
            <p v-if="companySaved" class="text-xs text-green-600 dark:text-green-400">
              <Check class="inline w-3.5 h-3.5" aria-hidden="true" /> Entreprise renommée
            </p>
          </div>

          <!-- First + Last name -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label
                for="edit-client-field-1"
                class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
              >
                Prénom <span class="text-red-500">*</span>
              </label>
              <input
                id="edit-client-field-1"
                v-model="form.first_name"
                required
                type="text"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label
                for="edit-client-field-2"
                class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
              >
                Nom <span class="text-slate-400 font-normal text-xs">(optionnel)</span>
              </label>
              <input
                id="edit-client-field-2"
                v-model="form.last_name"
                type="text"
                class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <!-- Email -->
          <div>
            <label
              for="edit-client-field-3"
              class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
              >Email</label
            >
            <input
              id="edit-client-field-3"
              v-model="form.email"
              type="email"
              class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 placeholder-slate-400"
              placeholder="contact@example.com"
            />
          </div>

          <AbsencePeriodFields
            v-model:start="form.absence_start_date"
            v-model:end="form.absence_end_date"
            id-prefix="edit-client-absence"
          />

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

<script setup lang="ts">
import { Check, X } from 'lucide-vue-next'
import { ref, reactive } from 'vue'
import { errorMessage } from '../api/index'
import { useClientStore } from '../stores/clientStore'
import AbsencePeriodFields from './AbsencePeriodFields.vue'
import type { Client } from '../types/api'

const props = defineProps<{ client: Client }>()
const emit = defineEmits<{ close: []; updated: [client: Client] }>()

const clientStore = useClientStore()

const form = reactive({
  first_name: props.client.first_name,
  last_name: props.client.last_name ?? '',
  email: props.client.email ?? '',
  absence_start_date: props.client.absence_start_date ?? '',
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
    setTimeout(() => {
      companySaved.value = false
    }, 2000)
  } catch (e) {
    companyName.value = props.client.company.name
    error.value = errorMessage(e, "Ce nom d'entreprise existe déjà.")
  } finally {
    savingCompany.value = false
  }
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    // Champ vidé = valeur effacée (null), pas ignorée.
    const payload = {
      first_name: form.first_name,
      last_name: form.last_name || null,
      email: form.email || null,
      absence_start_date: form.absence_start_date || null,
      absence_end_date: form.absence_end_date || null,
    }
    const updated = await clientStore.updateClient(props.client.id, payload)
    emit('updated', updated)
  } catch (e) {
    error.value = errorMessage(e, 'Erreur lors de la modification. Veuillez réessayer.')
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
