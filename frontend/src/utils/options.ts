// Options des menus déroulants, construites à partir des libellés partagés.
import type { SelectOption } from '../components/ui/BaseSelect.vue'
import type { PresenceStatus, TaskPriority, TaskStatus } from '../types/api'
import { PRESENCE, PRIORITY_LABELS, STATUS_LABELS } from './labels'

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
