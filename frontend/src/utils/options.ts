// Options des menus déroulants, construites à partir des libellés partagés.
import type { SelectOption } from '../components/ui/BaseSelect.vue'
import type { PresenceStatus, Recurrence, TaskPriority, TaskStatus } from '../types/api'
import { PRESENCE, PRIORITY_LABELS, RECURRENCE_LABELS, STATUS_LABELS } from './labels'

function entries<K extends string, V>(record: Record<K, V>): [K, V][] {
  return Object.entries(record) as [K, V][]
}

export const STATUS_OPTIONS: SelectOption<TaskStatus>[] = entries(STATUS_LABELS).map(([value, label]) => ({
  value,
  label,
}))

export const PRIORITY_OPTIONS: SelectOption<TaskPriority>[] = entries(PRIORITY_LABELS).map(
  ([value, label]) => ({ value, label }),
)

export const PRESENCE_OPTIONS: SelectOption<PresenceStatus>[] = entries(PRESENCE).map(([value, item]) => ({
  value,
  label: item.label,
  dot: item.color,
}))

/** '' : la tâche ne se répète pas. */
export const RECURRENCE_OPTIONS: SelectOption<Recurrence | ''>[] = [
  { value: '', label: 'Ne se répète pas' },
  ...entries(RECURRENCE_LABELS).map(([value, label]) => ({ value, label })),
]
