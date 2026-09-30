import { describe, expect, it } from 'vitest'
import { formatDate, formatLogValue, fullName, presenceLabel } from '../labels'
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
})
