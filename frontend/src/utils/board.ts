// Tableau Kanban : une colonne par statut.
import { tasksApi } from '../api/index'
import type { Task, TaskStatus, TaskSummary } from '../types/api'
import { daysBetween } from './dates'

export const BOARD_STATUSES: TaskStatus[] = ['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE']
/** La colonne « Terminé » ne garde que les tâches terminées récemment. */
export const DONE_DAYS = 14

export interface BoardColumn {
  status: TaskStatus
  tasks: TaskSummary[]
}

export function boardColumns(tasks: TaskSummary[], today: Date): BoardColumn[] {
  return BOARD_STATUSES.map((status) => {
    let column = tasks.filter((task) => task.status === status)
    if (status === 'DONE') {
      column = column
        .filter((task) => daysBetween(new Date(task.updated_at), today) <= DONE_DAYS)
        .sort((a, b) => b.updated_at.localeCompare(a.updated_at))
    }
    return { status, tasks: column }
  })
}

/**
 * Change le statut en passant par les bons endpoints : terminer utilise
 * /close (qui crée l'occurrence suivante d'une tâche récurrente), sortir de
 * « Terminé » utilise /reopen (qui repasse en « À faire »), puis le statut visé.
 */
export async function moveTask(id: string, from: TaskStatus, to: TaskStatus): Promise<Task> {
  if (to === 'DONE') return (await tasksApi.close(id)).data
  if (from === 'DONE') {
    const reopened = (await tasksApi.reopen(id)).data
    if (to === 'TODO') return reopened
  }
  return (await tasksApi.update(id, { status: to })).data
}
