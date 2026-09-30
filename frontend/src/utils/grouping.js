// Regroupement des tâches par jour d'échéance, dans l'ordre renvoyé par l'API
// (échéance, puis priorité).

const DAY_MS = 24 * 60 * 60 * 1000

function startOfDay(date) {
  const copy = new Date(date)
  copy.setHours(0, 0, 0, 0)
  return copy
}

function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export function dayLabel(dueDate, today = new Date()) {
  if (!dueDate) return 'Sans échéance'
  const due = startOfDay(new Date(`${dueDate}T00:00:00`))
  const diff = Math.round((due - startOfDay(today)) / DAY_MS)
  if (diff < 0) return `En retard — ${due.toLocaleDateString('fr-FR', { day: '2-digit', month: 'long' })}`
  if (diff === 0) return "Aujourd'hui"
  if (diff === 1) return 'Demain'
  if (diff <= 7) {
    return capitalize(due.toLocaleDateString('fr-FR', { weekday: 'long', day: '2-digit', month: 'long' }))
  }
  return due.toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
}

/** @returns {{ key: string, label: string, overdue: boolean, tasks: object[] }[]} */
export function groupTasksByDay(tasks, today = new Date()) {
  const groups = []
  const byKey = new Map()
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
