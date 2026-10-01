// Brouillon d'email de relance, ouvert dans le logiciel de messagerie (mailto:).
import type { TaskSummary, User } from '../types/api'
import { formatCompactDate, parseIsoDate } from './dates'

export interface FollowUpDraft {
  to: string
  subject: string
  body: string
}

export function followUpDraft(
  task: TaskSummary,
  sender: Pick<User, 'full_name'> | null,
): FollowUpDraft | null {
  const to = task.client.email
  if (!to) return null
  const due = parseIsoDate(task.due_date)
  const lines = [
    `Bonjour ${task.client.first_name},`,
    '',
    `Je reviens vers vous au sujet de « ${task.title} »${due ? ` (échéance prévue le ${formatCompactDate(due)})` : ''}.`,
    ...(task.description ? ['', task.description] : []),
    '',
    'Pourriez-vous me faire un retour ?',
    '',
    'Bien cordialement,',
    ...(sender?.full_name ? [sender.full_name] : []),
  ]
  return { to, subject: `Relance : ${task.title}`, body: lines.join('\n') }
}

/** Lien mailto: — sujet et corps encodés en RFC 3986 (espaces en %20, pas en +). */
export function mailtoHref(draft: FollowUpDraft): string {
  const query = `subject=${encodeURIComponent(draft.subject)}&body=${encodeURIComponent(draft.body)}`
  return `mailto:${encodeURIComponent(draft.to).replace('%40', '@')}?${query}`
}
