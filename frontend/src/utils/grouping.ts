// Regroupement des tâches par jour d'échéance, dans l'ordre renvoyé par l'API
// (échéance, puis priorité). Un seul format de titre : « Aujourd'hui »,
// « Demain », puis « Mercredi 7 octobre » (année seulement si elle diffère).

import type { TaskSummary } from '../types/api'
import { daysBetween, formatDayHeading, parseIsoDate, startOfDay } from './dates'

export interface TaskGroup<T extends TaskSummary = TaskSummary> {
  key: string
  label: string
  overdue: boolean
  tasks: T[]
}

export function dayLabel(dueDate: string | null, today: Date = new Date()): string {
  const due = parseIsoDate(dueDate)
  if (!due) return 'Sans échéance'
  const diff = daysBetween(today, due)
  if (diff === 0) return "Aujourd'hui"
  if (diff === 1) return 'Demain'
  return formatDayHeading(due, today)
}

export function groupTasksByDay<T extends TaskSummary>(tasks: T[], today: Date = new Date()): TaskGroup<T>[] {
  const groups: TaskGroup<T>[] = []
  const byKey = new Map<string, TaskGroup<T>>()
  const todayStart = startOfDay(today)
  for (const task of tasks) {
    // Toutes les tâches en retard forment un seul groupe, en tête.
    const due = parseIsoDate(task.due_date)
    const overdue = due !== null && due < todayStart
    const key = overdue ? 'overdue' : (task.due_date ?? 'none')
    let group = byKey.get(key)
    if (!group) {
      const label = overdue ? 'En retard' : dayLabel(task.due_date, today)
      group = { key, label, overdue, tasks: [] }
      byKey.set(key, group)
      groups.push(group)
    }
    group.tasks.push(task)
  }
  return groups
}
