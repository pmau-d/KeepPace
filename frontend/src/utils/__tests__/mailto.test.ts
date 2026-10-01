import { describe, expect, it } from 'vitest'
import { followUpDraft, mailtoHref } from '../mailto'
import { makeClient, makeTask } from '../../test/factories'

describe('brouillon de relance', () => {
  it("n'existe pas sans adresse email du client", () => {
    expect(followUpDraft(makeTask(), null)).toBeNull()
  })

  it('reprend le titre, l’échéance, la description et la signature', () => {
    const task = makeTask({
      title: 'Bon de commande',
      due_date: '2026-10-07',
      description: 'Version signée attendue.',
      client: makeClient({ first_name: 'Inès', email: 'ines@example.com' }),
    })
    const draft = followUpDraft(task, { full_name: 'Alex Martin' })!
    expect(draft.to).toBe('ines@example.com')
    expect(draft.subject).toBe('Relance : Bon de commande')
    expect(draft.body).toContain('Bonjour Inès,')
    expect(draft.body).toContain('« Bon de commande » (échéance prévue le mer. 7 oct.)')
    expect(draft.body).toContain('Version signée attendue.')
    expect(draft.body.endsWith('Bien cordialement,\nAlex Martin')).toBe(true)
  })

  it('encode le lien sans « + » à la place des espaces', () => {
    const href = mailtoHref({ to: 'a@example.com', subject: 'Relance : x & y', body: 'Ligne 1\nLigne 2' })
    expect(href).toBe('mailto:a@example.com?subject=Relance%20%3A%20x%20%26%20y&body=Ligne%201%0ALigne%202')
  })
})
