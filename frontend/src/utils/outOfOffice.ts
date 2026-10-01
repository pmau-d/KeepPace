// Extraction des dates d'un message d'absence collé (réponse automatique),
// en français ou en anglais : « absent du 3 au 17 octobre », « de retour le
// 20/10 », « back on October 20 », « jusqu'au 17.10.2026 »…
import type { IsoDate } from '../types/api'
import { addDays, startOfDay, toIsoDate } from './dates'
import { normalize } from './text'

export interface DetectedAbsence {
  start: IsoDate | null
  end: IsoDate | null
}

const MONTHS: Record<string, number> = {
  janvier: 1,
  janv: 1,
  january: 1,
  jan: 1,
  fevrier: 2,
  fevr: 2,
  fev: 2,
  february: 2,
  feb: 2,
  mars: 3,
  march: 3,
  mar: 3,
  avril: 4,
  avr: 4,
  april: 4,
  apr: 4,
  mai: 5,
  may: 5,
  juin: 6,
  june: 6,
  jun: 6,
  juillet: 7,
  juil: 7,
  july: 7,
  jul: 7,
  aout: 8,
  august: 8,
  aug: 8,
  septembre: 9,
  sept: 9,
  september: 9,
  sep: 9,
  octobre: 10,
  oct: 10,
  october: 10,
  novembre: 11,
  nov: 11,
  november: 11,
  decembre: 12,
  dec: 12,
  december: 12,
}
const MONTH = `(${Object.keys(MONTHS)
  .sort((a, b) => b.length - a.length)
  .join('|')})\\.?`
const DAY = '(\\d{1,2})(?:er|st|nd|rd|th)?'
const YEAR = '(?:\\s+(\\d{4}))?'
// Une date : « 3 octobre 2026 », « October 3, 2026 », « 03/10/2026 », « 3.10 », « 2026-10-03 »
const DATE = [
  `(\\d{4})-(\\d{2})-(\\d{2})`,
  `${DAY}[/.-](\\d{1,2})(?:[/.-](\\d{2,4}))?`,
  `${DAY}\\s+${MONTH}${YEAR}`,
  `${MONTH}\\s+${DAY},?${YEAR}`,
].join('|')

interface RawDate {
  day: number
  month: number
  year: number | null
}

function readDate(text: string): RawDate | null {
  const m = new RegExp(`^(?:${DATE})$`).exec(text.trim())
  if (!m) return null
  if (m[1]) return { year: Number(m[1]), month: Number(m[2]), day: Number(m[3]) }
  if (m[4]) {
    const year = m[6] ? Number(m[6].length === 2 ? `20${m[6]}` : m[6]) : null
    return { day: Number(m[4]), month: Number(m[5]), year }
  }
  if (m[7]) return { day: Number(m[7]), month: MONTHS[m[8]!]!, year: m[9] ? Number(m[9]) : null }
  return { day: Number(m[11]), month: MONTHS[m[10]!]!, year: m[12] ? Number(m[12]) : null }
}

/** Sans année : la prochaine occurrence (un message d'absence parle du présent ou du futur proche). */
function toDate(raw: RawDate, today: Date, notBefore?: Date): Date | null {
  if (raw.month < 1 || raw.month > 12 || raw.day < 1 || raw.day > 31) return null
  const build = (year: number) => new Date(year, raw.month - 1, raw.day)
  if (raw.year) return build(raw.year)
  let date = build(today.getFullYear())
  const floor = notBefore ?? addDays(today, -30)
  if (date < floor) date = build(today.getFullYear() + 1)
  return date
}

// Pour repérer une date dans une phrase, sans capturer ses morceaux (lus ensuite par readDate).
const ANY_DATE = DATE.replace(/\((?!\?)/g, '(?:')
// « lundi 20 octobre », « Monday, October 20 » : le jour de la semaine est ignoré
const WEEKDAY =
  '(?:(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|monday|tuesday|wednesday|thursday|friday|saturday|sunday),?\\s+)?'

const RULES: { pattern: RegExp; kind: 'range' | 'until' | 'back' }[] = [
  // « du 3 octobre au 17 octobre », « du 3 au 17 octobre », « from 3 to 17 October »
  {
    pattern: new RegExp(
      `(?:du|from|entre le|between)\\s+${WEEKDAY}(${ANY_DATE}|\\d{1,2})\\s+(?:au|to|until|till|et le|and)\\s+${WEEKDAY}(${ANY_DATE})`,
    ),
    kind: 'range',
  },
  // « de retour le 20 octobre », « back on October 20 », « retour prévu le 20/10 »
  {
    pattern: new RegExp(
      `(?:de retour|retour(?: prevu)?|back|return(?:ing)?)\\s+(?:au bureau\\s+|in the office\\s+)?(?:le\\s+|on\\s+)?${WEEKDAY}(${ANY_DATE})`,
    ),
    kind: 'back',
  },
  // « jusqu'au 17 octobre », « until October 17 »
  {
    pattern: new RegExp(`(?:jusqu'?au|jusqu'?a|until|till|through)\\s+(?:le\\s+)?${WEEKDAY}(${ANY_DATE})`),
    kind: 'until',
  },
]

/**
 * Dates d'absence trouvées dans le message, ou null si aucune formulation
 * reconnue. `end` est le dernier jour d'absence (un « retour le 20 » donne le 19).
 */
export function detectAbsence(message: string, today: Date = new Date()): DetectedAbsence | null {
  const text = normalize(message).replace(/’/g, "'")
  const day0 = startOfDay(today)
  for (const { pattern, kind } of RULES) {
    const match = pattern.exec(text)
    if (!match) continue
    if (kind === 'range') {
      const second = readDate(match[2] ?? '')
      const firstText = match[1] ?? ''
      // « du 3 au 17 octobre » : le premier jour reprend le mois (et l'année) du second
      const first =
        /^\d{1,2}$/.test(firstText) && second ? { ...second, day: Number(firstText) } : readDate(firstText)
      if (!first || !second) continue
      const start = toDate(first, day0)
      const end = start && toDate({ ...second, year: second.year ?? first.year }, day0, start)
      if (start && end && end >= start) return { start: toIsoDate(start), end: toIsoDate(end) }
    } else {
      const raw = readDate(match[1] ?? '')
      const date = raw && toDate(raw, day0)
      if (!date) continue
      // « de retour le 20 » : absent jusqu'au 19 inclus
      return { start: null, end: toIsoDate(kind === 'back' ? addDays(date, -1) : date) }
    }
  }
  return null
}
