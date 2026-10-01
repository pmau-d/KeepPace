import { describe, expect, it } from 'vitest'
import { formatDate, formatLogValue, fullName, presenceLabel, presenceNote } from '../labels'
import { makeLog } from '../../test/factories'
import type { PresenceStatus } from '../../types/api'

describe('labels', () => {
  it('formate une date sans décalage de fuseau', () => {
    expect(formatDate('2026-10-01')).toBe('01/10/2026')
  })

  it('compose le nom complet', () => {
    expect(fullName({ first_name: 'Alice', last_name: null })).toBe('Alice')
    expect(fullName({ first_name: 'Alice', last_name: 'Martin' })).toBe('Alice Martin')
  })

  it("rend lisibles les valeurs de l'historique", () => {
    expect(formatLogValue(makeLog({ field_changed: 'status', new_value: 'BLOCKED' }), 'new')).toBe(
      'En attente client',
    )
    expect(
      formatLogValue(
        makeLog({ field_changed: 'client_id', old_value: 'uuid', old_label: 'Bob · Globex' }),
        'old',
      ),
    ).toBe('Bob · Globex')
    expect(formatLogValue(makeLog({ field_changed: 'archived', new_value: 'true' }), 'new')).toBe('Archivée')
    expect(formatLogValue(makeLog({ field_changed: 'archived', old_value: null }), 'old')).toBeNull()
  })

  it('connaît tous les statuts de présence', () => {
    expect(presenceLabel('LEAVING_SOON')).toBe('Bientôt absent')
    expect(presenceLabel('???' as PresenceStatus)).toBe('Inconnu')
    expect(presenceLabel(null)).toBe('Inconnu')
  })

  it('explique la présence d’un client sur ses tâches', () => {
    const today = new Date('2026-10-01T10:00:00')
    const note = (presence_status: PresenceStatus, start: string | null, end: string | null) =>
      presenceNote({ presence_status, absence_start_date: start, absence_end_date: end }, today)
    expect(note('PRESENT', null, null)).toBeNull()
    expect(note('ABSENT', '2026-09-20', '2026-10-10')).toBe("Absent jusqu'au sam. 10 oct.")
    expect(note('ABSENT', '2026-09-20', null)).toBe('Absent, retour non daté')
    expect(note('LEAVING_SOON', '2026-10-03', '2026-10-20')).toBe('Part le sam. 3 oct.')
    expect(note('SOON_BACK', null, '2026-10-02')).toBe('De retour le sam. 3 oct.')
    expect(note('RECENTLY_BACK', null, '2026-09-28')).toBe('Rentré le mar. 29 sept.')
  })
})
