import { describe, expect, it } from 'vitest'
import { confirm, useConfirmDialog } from '../useConfirm.js'

describe('confirm', () => {
  it('se résout selon le choix', async () => {
    const dialog = useConfirmDialog()
    const accepted = confirm({ title: 'Archiver ?' })
    expect(dialog.state.open).toBe(true)
    expect(dialog.state.title).toBe('Archiver ?')
    dialog.accept()
    await expect(accepted).resolves.toBe(true)

    const cancelled = confirm({ title: 'Supprimer ?' })
    dialog.cancel()
    await expect(cancelled).resolves.toBe(false)
    expect(dialog.state.open).toBe(false)
  })

  it('une nouvelle demande annule la précédente', async () => {
    const first = confirm({ title: 'A' })
    const second = confirm({ title: 'B' })
    await expect(first).resolves.toBe(false)
    useConfirmDialog().accept()
    await expect(second).resolves.toBe(true)
  })
})
