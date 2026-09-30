// Regroupement des tâches par jour d'échéance, dans l'ordre renvoyé par l'API
// (échéance, puis priorité).

import type { TaskSummary } from '../types/api'

export interface TaskGroup<T extends TaskSummary = TaskSummary> {
  key: string
  label: string
  overdue: boolean
  tasks: T[]
}

const DAY_MS = 24 * 60 * 60 * 1000

function startOfDay(date: Date | string | number): Date {
  const copy = new Date(date)
  copy.setHours(0, 0, 0, 0)
  return copy
}

function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export function dayLabel(dueDate: string | null, today: Date = new Date()): string {
  if (!dueDate) return 'Sans échéance'
  const due = startOfDay(new Date(`${dueDate}T00:00:00`))
  const diff = Math.round((due.getTime() - startOfDay(today).getTime()) / DAY_MS)
  if (diff < 0) return `En retard — ${due.toLocaleDateString('fr-FR', { day: '2-digit', month: 'long' })}`
  if (diff === 0) return "Aujourd'hui"
  if (diff === 1) return 'Demain'
  if (diff <= 7) {
    return capitalize(due.toLocaleDateString('fr-FR', { weekday: 'long', day: '2-digit', month: 'long' }))
  }
  return due.toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
}

export function groupTasksByDay<T extends TaskSummary>(tasks: T[], today: Date = new Date()): TaskGroup<T>[] {
  const groups: TaskGroup<T>[] = []
  const byKey = new Map<string, TaskGroup<T>>()
  const todayStart = startOfDay(today)
  for (const task of tasks) {
    // Toutes les tâches en retard forment un seul groupe, en tête.
    const overdue = Boolean(task.due_date) && new Date(`${task.due_date}T00:00:00`) < todayStart
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
