<template>
  <div class="p-5">
    <ChecklistEditor
      :items="items"
      :can-finish="canFinish"
      id-prefix="task-checklist"
      @add="add"
      @toggle="toggle"
      @remove="remove"
      @finish="$emit('finish')"
    />
  </div>
</template>

<script setup lang="ts">
import { tasksApi } from '../../api/index'
import { useToastStore } from '../../stores/toast'
import ChecklistEditor from './ChecklistEditor.vue'
import type { ChecklistItem } from '../../types/api'

const props = defineProps<{ taskId: string; items: ChecklistItem[]; canFinish: boolean }>()
const emit = defineEmits<{ 'update:items': [items: ChecklistItem[]]; changed: []; finish: [] }>()

const toast = useToastStore()

async function run(action: () => Promise<ChecklistItem[]>, failure: string) {
  try {
    emit('update:items', await action())
    emit('changed')
  } catch (e) {
    toast.error(e, failure)
  }
}

const add = (label: string) =>
  run(async () => {
    const item = (await tasksApi.addChecklistItem(props.taskId, label)).data
    return [...props.items, item]
  }, "Impossible d'ajouter la case.")

const toggle = (item: ChecklistItem) =>
  run(async () => {
    const updated = (await tasksApi.updateChecklistItem(props.taskId, item.id, { done: !item.done })).data
    return props.items.map((i) => (i.id === item.id ? updated : i))
  }, 'Impossible de modifier la case.')

const remove = (item: ChecklistItem) =>
  run(async () => {
    await tasksApi.deleteChecklistItem(props.taskId, item.id)
    return props.items.filter((i) => i.id !== item.id)
  }, 'Impossible de supprimer la case.')
</script>
