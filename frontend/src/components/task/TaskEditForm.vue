<template>
  <form class="p-5 space-y-4" @submit.prevent="save">
    <div>
      <label for="task-title" :class="labelClass">Titre</label>
      <input id="task-title" v-model="form.title" type="text" required maxlength="200" :class="inputClass" />
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label for="task-status" :class="labelClass">Statut</label>
        <BaseSelect id="task-status" v-model="form.status" :options="STATUS_OPTIONS" block />
      </div>
      <div>
        <label for="task-priority" :class="labelClass">Priorité</label>
        <BaseSelect id="task-priority" v-model="form.priority" :options="PRIORITY_OPTIONS" block />
      </div>
    </div>

    <div>
      <label for="task-sub-status" :class="labelClass">
        Statut personnalisé
        <span class="font-normal text-slate-400">(optionnel — ex. : en attente du fournisseur)</span>
      </label>
      <input
        id="task-sub-status"
        v-model="form.sub_status"
        type="text"
        list="sub-status-suggestions"
        maxlength="200"
        :class="inputClass"
        placeholder="Ex. : En attente du fournisseur…"
      />
      <datalist id="sub-status-suggestions">
        <option v-for="s in SUB_STATUS_SUGGESTIONS" :key="s" :value="s" />
      </datalist>
      <div class="flex flex-wrap gap-1.5 mt-2">
        <button
          v-for="s in QUICK_SUB_STATUSES"
          :key="s"
          type="button"
          :aria-pressed="form.sub_status === s"
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

    <div>
      <label for="task-due" :class="labelClass">Date d'échéance</label>
      <DatePicker id="task-due" v-model="form.due_date" placeholder="Sans échéance" />
    </div>

    <div>
      <label for="task-description" :class="labelClass">Description</label>
      <textarea
        id="task-description"
        v-model="form.description"
        rows="3"
        :class="[inputClass, 'resize-none']"
        placeholder="Description…"
      ></textarea>
    </div>

    <div>
      <label for="task-log-comment" :class="labelClass">Note de modification (historique)</label>
      <input
        id="task-log-comment"
        v-model="form.comment"
        type="text"
        :class="inputClass"
        placeholder="Raison de la modification…"
      />
    </div>

    <button
      type="submit"
      :disabled="saving || !isDirty"
      class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-sm py-2.5 rounded-lg transition-colors"
    >
      {{ saving ? 'Enregistrement…' : isDirty ? 'Enregistrer' : 'Aucune modification' }}
    </button>

    <section
      v-if="task.status !== 'DONE'"
      class="pt-3 border-t border-slate-200 dark:border-slate-700 space-y-2"
      aria-labelledby="follow-up-title"
    >
      <p id="follow-up-title" :class="[labelClass, 'flex items-center gap-1.5']">
        <AlarmClock class="w-3.5 h-3.5" aria-hidden="true" /> Relancer dans
      </p>
      <div class="grid grid-cols-4 gap-1.5">
        <button
          v-for="option in SNOOZE_OPTIONS"
          :key="option.days"
          type="button"
          :disabled="busy"
          :title="`Nouvelle échéance : ${snoozeTarget(option.days)}`"
          class="text-xs font-medium py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-300 transition-colors disabled:opacity-50"
          @click="snooze(option.days)"
        >
          {{ option.label }}
        </button>
      </div>
      <a
        v-if="mailto"
        :href="mailto"
        class="flex items-center justify-center gap-2 text-sm font-medium py-2 rounded-lg border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
      >
        <Mail class="w-4 h-4" aria-hidden="true" /> Rédiger une relance à {{ task.client.first_name }}
      </a>
      <p v-else class="text-xs text-slate-400 flex items-center gap-1.5">
        <Mail class="w-3.5 h-3.5" aria-hidden="true" />
        Ajoutez l'email du client pour rédiger une relance en un clic.
      </p>
    </section>

    <div class="pt-3 border-t border-slate-200 dark:border-slate-700 grid grid-cols-2 gap-2">
      <button
        v-if="task.status !== 'DONE'"
        type="button"
        :disabled="busy"
        class="flex items-center justify-center gap-2 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-900/20 dark:hover:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 font-medium text-sm py-2 rounded-lg transition-colors disabled:opacity-50"
        @click="run(() => taskStore.closeTask(task.id), 'Tâche terminée.')"
      >
        <Check class="w-4 h-4" aria-hidden="true" /> Terminer
      </button>
      <button
        v-else
        type="button"
        :disabled="busy"
        class="flex items-center justify-center gap-2 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/40 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800 font-medium text-sm py-2 rounded-lg transition-colors disabled:opacity-50"
        @click="run(() => taskStore.reopenTask(task.id), 'Tâche réouverte.')"
      >
        <RotateCcw class="w-4 h-4" aria-hidden="true" /> Réouvrir
      </button>
      <button
        type="button"
        class="flex items-center justify-center gap-2 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-900/20 dark:hover:bg-indigo-900/40 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 font-medium text-sm py-2 rounded-lg transition-colors"
        @click="$emit('duplicate')"
      >
        <Copy class="w-4 h-4" aria-hidden="true" /> Dupliquer
      </button>
    </div>

    <div class="pt-3 border-t border-slate-200 dark:border-slate-700">
      <button
        type="button"
        :disabled="busy"
        class="w-full border border-red-300 dark:border-red-800 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 font-medium text-sm py-2 rounded-lg transition-colors disabled:opacity-50"
        @click="archive"
      >
        Archiver la tâche
      </button>
      <p class="text-xs text-slate-400 text-center mt-1">Réversible : l'historique est conservé.</p>
    </div>
  </form>
</template>

<script setup lang="ts">
import { AlarmClock, Check, Copy, Mail, RotateCcw } from '@lucide/vue'
import { computed, reactive, ref, watch } from 'vue'
import { confirm } from '../../composables/useConfirm'
import { useAuthStore } from '../../stores/auth'
import { useTaskStore } from '../../stores/taskStore'
import { useToastStore } from '../../stores/toast'
import BaseSelect from '../ui/BaseSelect.vue'
import DatePicker from '../ui/DatePicker.vue'
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../../utils/options'
import { addDays, formatCompactDate } from '../../utils/dates'
import { followUpDraft, mailtoHref } from '../../utils/mailto'
import type { Task, TaskPriority, TaskStatus, TaskSummary, TaskUpdatePayload } from '../../types/api'

const props = defineProps<{ task: Task }>()
const emit = defineEmits<{ updated: [task: TaskSummary]; duplicate: []; archived: [] }>()

const taskStore = useTaskStore()
const toast = useToastStore()
const auth = useAuthStore()

const SNOOZE_OPTIONS = [
  { days: 1, label: 'Demain' },
  { days: 3, label: '3 jours' },
  { days: 7, label: '1 sem.' },
  { days: 14, label: '2 sem.' },
]
const snoozeTarget = (days: number) => formatCompactDate(addDays(new Date(), days))
const mailto = computed(() => {
  const draft = followUpDraft(props.task, auth.user)
  return draft ? mailtoHref(draft) : null
})

const SUB_STATUS_SUGGESTIONS = [
  'En attente du client',
  'En attente du fournisseur',
  'En attente de validation',
  'En attente du service informatique',
  'En attente de chiffrage',
  'En attente de livraison',
  'En cours de relecture',
  'Bloqué — dépendance externe',
]
const QUICK_SUB_STATUSES = SUB_STATUS_SUGGESTIONS.slice(0, 4)

const labelClass = 'block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1'
const inputClass =
  'w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 placeholder-slate-400'

const EDITABLE = ['title', 'status', 'priority', 'sub_status', 'due_date', 'description'] as const
type EditableField = (typeof EDITABLE)[number]

interface EditForm {
  title: string
  status: TaskStatus
  priority: TaskPriority
  sub_status: string
  due_date: string
  description: string
  comment: string
}

const form = reactive<EditForm>(formFrom(props.task))
const saving = ref(false)
const busy = ref(false)

function formFrom(task: Task): EditForm {
  return {
    title: task.title,
    status: task.status,
    priority: task.priority,
    sub_status: task.sub_status ?? '',
    due_date: task.due_date ?? '',
    description: task.description ?? '',
    comment: '',
  }
}
watch(
  () => props.task,
  (task) => Object.assign(form, formFrom(task)),
)

/** Champs réellement modifiés (chaînes vides envoyées comme null). */
const changes = computed<TaskUpdatePayload>(() => {
  const diff: Record<string, string | null> = {}
  for (const field of EDITABLE satisfies readonly EditableField[]) {
    const value = form[field] === '' ? null : form[field]
    if (value !== (props.task[field] ?? null)) diff[field] = value
  }
  return diff as TaskUpdatePayload
})
const isDirty = computed(() => Object.keys(changes.value).length > 0)

async function save() {
  if (!isDirty.value) return
  if (!form.title.trim()) {
    toast.error('Le titre est obligatoire.')
    return
  }
  saving.value = true
  try {
    const payload = { ...changes.value }
    if (form.comment.trim()) payload.comment = form.comment.trim()
    emit('updated', await taskStore.updateTask(props.task.id, payload))
    toast.success('Modifications enregistrées.')
  } catch (error) {
    toast.error(error, "Impossible d'enregistrer les modifications.")
  } finally {
    saving.value = false
  }
}

async function run(action: () => Promise<TaskSummary>, successMessage: string) {
  busy.value = true
  try {
    emit('updated', await action())
    toast.success(successMessage)
  } catch (error) {
    toast.error(error)
  } finally {
    busy.value = false
  }
}

async function snooze(days: number) {
  const note = form.comment.trim() || undefined
  await run(() => taskStore.snoozeTask(props.task.id, days, note), `Relance prévue le ${snoozeTarget(days)}`)
}

async function archive() {
  const ok = await confirm({
    title: `Archiver « ${props.task.title} » ?`,
    message: 'La tâche disparaît des listes mais reste consultable et restaurable depuis les Archives.',
    confirmLabel: 'Archiver',
    danger: true,
  })
  if (!ok) return
  busy.value = true
  try {
    const { id, title } = props.task
    await taskStore.archiveTask(id)
    emit('archived')
    toast.success(`« ${title} » archivée.`, {
      action: { label: 'Annuler', run: () => taskStore.restoreTask(id) },
    })
  } catch (error) {
    toast.error(error)
  } finally {
    busy.value = false
  }
}
</script>
