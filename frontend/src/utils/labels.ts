// Libellés et formats d'affichage partagés (badges, historique, filtres).

import type { FollowUpReason, PresenceStatus, TaskLog, TaskPriority, TaskStatus } from '../types/api'

export const STATUS_LABELS: Record<TaskStatus, string> = {
  TODO: 'À faire',
  IN_PROGRESS: 'En cours',
  BLOCKED: 'En attente client',
  DONE: 'Terminé',
}

export const PRIORITY_LABELS: Record<TaskPriority, string> = {
  HIGH: 'Haute',
  MEDIUM: 'Moyenne',
  LOW: 'Basse',
}

interface LabelColor {
  label: string
  color: string
}

export const PRESENCE: Record<PresenceStatus, LabelColor> = {
  PRESENT: { label: 'Présent', color: 'bg-green-500' },
  LEAVING_SOON: { label: 'Bientôt absent', color: 'bg-orange-500' },
  ABSENT: { label: 'Absent', color: 'bg-red-500' },
  SOON_BACK: { label: 'Bientôt de retour', color: 'bg-yellow-400' },
  RECENTLY_BACK: { label: 'Rentré récemment', color: 'bg-blue-500' },
}

export const FOLLOW_UP_REASONS: Record<FollowUpReason, LabelColor> = {
  OVERDUE: { label: 'Échéance dépassée', color: 'text-red-600 dark:text-red-400' },
  DUE_TODAY: { label: "Échéance aujourd'hui", color: 'text-amber-600 dark:text-amber-400' },
  CLIENT_LEAVING: { label: 'Le client part bientôt', color: 'text-orange-600 dark:text-orange-400' },
  CLIENT_BACK: { label: 'Le client vient de rentrer', color: 'text-blue-600 dark:text-blue-400' },
  WAITING: { label: 'En attente sans nouvelle', color: 'text-violet-600 dark:text-violet-400' },
}

const FIELD_LABELS: Record<string, string> = {
  status: 'Statut',
  sub_status: 'Statut personnalisé',
  due_date: "Date d'échéance",
  description: 'Description',
  priority: 'Priorité',
  title: 'Titre',
  client_id: 'Client',
  archived: 'Archivage',
  comment: 'Commentaire',
}

/** Une valeur inattendue (nouvelle version de l'API) ne doit pas casser l'affichage. */
function presence(status: PresenceStatus | null | undefined): LabelColor | undefined {
  return status ? (PRESENCE as Partial<Record<string, LabelColor>>)[status] : undefined
}

export function presenceLabel(status: PresenceStatus | null | undefined): string {
  return presence(status)?.label ?? 'Inconnu'
}

export function presenceColor(status: PresenceStatus | null | undefined): string {
  return presence(status)?.color ?? 'bg-slate-400'
}

export function fullName(
  client: { first_name: string; last_name: string | null } | null | undefined,
): string {
  if (!client) return ''
  return [client.first_name, client.last_name].filter(Boolean).join(' ')
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return ''
  // Les dates sans heure (AAAA-MM-JJ) sont lues en heure locale, pas en UTC.
  const date = /^\d{4}-\d{2}-\d{2}$/.test(value) ? new Date(`${value}T00:00:00`) : new Date(value)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function fieldLabel(field: string): string {
  return FIELD_LABELS[field] ?? field
}

/** Valeur lisible d'une entrée d'historique ; `side` vaut 'old' ou 'new'. */
export function formatLogValue(log: TaskLog, side: 'old' | 'new'): string | null {
  const label = side === 'old' ? log.old_label : log.new_label
  if (label) return label
  const value = side === 'old' ? log.old_value : log.new_value
  if (value == null) return null
  switch (log.field_changed) {
    case 'status':
      return STATUS_LABELS[value as TaskStatus] ?? value
    case 'priority':
      return PRIORITY_LABELS[value as TaskPriority] ?? value
    case 'due_date':
      return formatDate(value)
    case 'archived':
      return value === 'true' ? 'Archivée' : null
    default:
      return value
  }
}
