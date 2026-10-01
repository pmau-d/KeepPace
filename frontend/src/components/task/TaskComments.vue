<template>
  <div class="flex flex-col h-full">
    <div class="flex-1 overflow-y-auto p-5 space-y-3">
      <div v-if="!comments.length" class="text-slate-400 text-sm py-8 text-center">
        <p>Aucun commentaire pour l'instant.</p>
      </div>
      <div v-for="c in comments" :key="c.id" class="group flex gap-3">
        <div
          class="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center shrink-0 mt-0.5 text-xs"
        >
          <MessageSquare class="w-3.5 h-3.5 text-indigo-500" aria-hidden="true" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="bg-slate-50 dark:bg-slate-700/50 rounded-xl px-3 py-2">
            <p class="text-sm text-slate-700 dark:text-slate-200 whitespace-pre-wrap break-words">
              {{ c.content }}
            </p>
          </div>
          <div class="flex items-center justify-between mt-1 px-1">
            <p class="text-xs text-slate-400">{{ formatDateTime(c.created_at) }}</p>
            <button
              class="opacity-0 group-hover:opacity-100 focus:opacity-100 text-xs text-red-400 hover:text-red-600 transition-all"
              @click="remove(c)"
            >
              Supprimer
            </button>
          </div>
        </div>
      </div>
    </div>

    <form class="p-4 border-t border-slate-200 dark:border-slate-700" @submit.prevent="submit">
      <label for="new-comment" class="sr-only">Nouveau commentaire</label>
      <div class="flex gap-2">
        <textarea
          id="new-comment"
          v-model="draft"
          rows="2"
          maxlength="10000"
          class="flex-1 text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 resize-none placeholder-slate-400"
          placeholder="Écrire un commentaire…"
          @keydown.ctrl.enter="submit"
          @keydown.meta.enter="submit"
        ></textarea>
        <button
          type="submit"
          :disabled="!draft.trim() || posting"
          aria-label="Envoyer le commentaire"
          class="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-xl transition-colors shrink-0"
        >
          <Send class="w-4 h-4" aria-hidden="true" />
        </button>
      </div>
      <p class="text-xs text-slate-400 mt-1">Ctrl+Entrée (⌘+Entrée) pour envoyer</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { MessageSquare, Send } from '@lucide/vue'
import { ref } from 'vue'
import { tasksApi } from '../../api/index'
import { confirm } from '../../composables/useConfirm'
import { useToastStore } from '../../stores/toast'
import { formatDateTime } from '../../utils/labels'
import type { TaskComment } from '../../types/api'

const props = defineProps<{ taskId: string; comments: TaskComment[] }>()
const emit = defineEmits<{ 'update:comments': [comments: TaskComment[]]; changed: [] }>()

const toast = useToastStore()
const draft = ref('')
const posting = ref(false)

async function submit() {
  if (!draft.value.trim() || posting.value) return
  posting.value = true
  try {
    const { data } = await tasksApi.addComment(props.taskId, draft.value.trim())
    emit('update:comments', [...props.comments, data])
    emit('changed')
    draft.value = ''
  } catch (error) {
    toast.error(error, "Impossible d'ajouter le commentaire.")
  } finally {
    posting.value = false
  }
}

async function remove(comment: TaskComment) {
  const ok = await confirm({
    title: 'Supprimer ce commentaire ?',
    message: "Son contenu restera visible dans l'historique de la tâche.",
    confirmLabel: 'Supprimer',
    danger: true,
  })
  if (!ok) return
  try {
    await tasksApi.deleteComment(props.taskId, comment.id)
    emit(
      'update:comments',
      props.comments.filter((c) => c.id !== comment.id),
    )
    emit('changed')
  } catch (error) {
    toast.error(error)
  }
}
</script>
