<template>
  <div class="fixed inset-0 z-60 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/50 backdrop-blur-xs" @click="$emit('close')"></div>

    <div
      class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-sm z-10 overflow-hidden"
      role="dialog"
      aria-modal="true"
      aria-labelledby="new-project-title"
      @keydown.esc="$emit('close')"
    >
      <div
        class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700"
      >
        <div>
          <h2 id="new-project-title" class="text-base font-semibold text-slate-800 dark:text-slate-100">
            Nouveau projet
          </h2>
          <p class="text-xs text-slate-400 mt-0.5">Un projet de développement, avec ses tâches et ses bugs</p>
        </div>
        <button
          type="button"
          class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 transition-colors"
          aria-label="Fermer"
          @click="$emit('close')"
        >
          <X class="w-4 h-4" aria-hidden="true" />
        </button>
      </div>

      <form class="px-6 py-5 space-y-4" @submit.prevent="submit">
        <div>
          <label
            for="new-project-name"
            class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
          >
            Nom <span class="text-red-500">*</span>
          </label>
          <input
            id="new-project-name"
            ref="nameInput"
            v-model="form.name"
            required
            maxlength="200"
            type="text"
            class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label
            for="new-project-description"
            class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
          >
            Description <span class="text-slate-400 font-normal text-xs">(optionnelle)</span>
          </label>
          <textarea
            id="new-project-description"
            v-model="form.description"
            rows="3"
            class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 resize-none"
          ></textarea>
        </div>

        <div>
          <label
            for="new-project-status"
            class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >État</label
          >
          <BaseSelect id="new-project-status" v-model="form.status" :options="STATUS_OPTIONS" block />
        </div>

        <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

        <button
          type="submit"
          :disabled="submitting || !form.name.trim()"
          class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm py-2.5 rounded-lg transition-colors"
        >
          {{ submitting ? 'Création…' : 'Créer le projet' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { X } from '@lucide/vue'
import { onMounted, reactive, ref } from 'vue'
import { errorMessage } from '../api/index'
import { useProjectStore } from '../stores/projectStore'
import { PROJECT_STATUS_LABELS } from '../utils/labels'
import BaseSelect from './ui/BaseSelect.vue'
import type { Project, ProjectStatus } from '../types/api'

const emit = defineEmits<{ close: []; created: [project: Project] }>()
const projectStore = useProjectStore()

const STATUS_OPTIONS = (Object.keys(PROJECT_STATUS_LABELS) as ProjectStatus[]).map((value) => ({
  value,
  label: PROJECT_STATUS_LABELS[value],
}))

const form = reactive<{ name: string; description: string; status: ProjectStatus }>({
  name: '',
  description: '',
  status: 'ACTIVE',
})
const nameInput = ref<HTMLInputElement | null>(null)
const submitting = ref(false)
const error = ref('')

onMounted(() => nameInput.value?.focus())

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const project = await projectStore.createProject({
      name: form.name.trim(),
      status: form.status,
      ...(form.description.trim() ? { description: form.description.trim() } : {}),
    })
    emit('created', project)
  } catch (e) {
    error.value = errorMessage(e, 'Erreur lors de la création du projet. Veuillez réessayer.')
  } finally {
    submitting.value = false
  }
}
</script>
