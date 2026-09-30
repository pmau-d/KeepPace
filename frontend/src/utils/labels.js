// Libellés et formats d'affichage partagés (badges, historique, filtres).

export const STATUS_LABELS = {
  TODO: 'À faire',
  IN_PROGRESS: 'En cours',
  BLOCKED: 'En attente client',
  DONE: 'Terminé',
}

export const PRIORITY_LABELS = { HIGH: 'Haute', MEDIUM: 'Moyenne', LOW: 'Basse' }

export const PRESENCE = {
  PRESENT: { label: 'Présent', color: 'bg-green-500' },
  LEAVING_SOON: { label: 'Bientôt absent', color: 'bg-orange-500' },
  ABSENT: { label: 'Absent', color: 'bg-red-500' },
  SOON_BACK: { label: 'Bientôt de retour', color: 'bg-yellow-400' },
  RECENTLY_BACK: { label: 'Rentré récemment', color: 'bg-blue-500' },
}

export const FOLLOW_UP_REASONS = {
  OVERDUE: { label: 'Échéance dépassée', color: 'text-red-600 dark:text-red-400' },
  DUE_TODAY: { label: "Échéance aujourd'hui", color: 'text-amber-600 dark:text-amber-400' },
  CLIENT_LEAVING: { label: 'Le client part bientôt', color: 'text-orange-600 dark:text-orange-400' },
  CLIENT_BACK: { label: 'Le client vient de rentrer', color: 'text-blue-600 dark:text-blue-400' },
  WAITING: { label: 'En attente sans nouvelle', color: 'text-violet-600 dark:text-violet-400' },
}

const FIELD_LABELS = {
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

export function presenceLabel(status) {
  return PRESENCE[status]?.label ?? 'Inconnu'
}

export function presenceColor(status) {
  return PRESENCE[status]?.color ?? 'bg-slate-400'
}

export function fullName(client) {
  if (!client) return ''
  return [client.first_name, client.last_name].filter(Boolean).join(' ')
}

export function formatDate(value) {
  if (!value) return ''
  // Les dates sans heure (AAAA-MM-JJ) sont lues en heure locale, pas en UTC.
  const date = /^\d{4}-\d{2}-\d{2}$/.test(value) ? new Date(`${value}T00:00:00`) : new Date(value)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export function formatDateTime(value) {
  return new Date(value).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function fieldLabel(field) {
  return FIELD_LABELS[field] ?? field
}

/** Valeur lisible d'une entrée d'historique ; `side` vaut 'old' ou 'new'. */
export function formatLogValue(log, side) {
  const label = log[`${side}_label`]
  if (label) return label
  const value = log[`${side}_value`]
  if (value == null) return null
  switch (log.field_changed) {
    case 'status':
      return STATUS_LABELS[value] ?? value
    case 'priority':
      return PRIORITY_LABELS[value] ?? value
    case 'due_date':
      return formatDate(value)
    case 'archived':
      return value === 'true' ? 'Archivée' : null
    default:
      return value
  }
}
