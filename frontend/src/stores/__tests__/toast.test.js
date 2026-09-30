import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useToastStore } from '../toast.js'

describe('toasts', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  it('disparaissent seuls après leur délai', () => {
    const toast = useToastStore()
    toast.success('Enregistré')
    expect(toast.toasts).toHaveLength(1)
    vi.advanceTimersByTime(4000)
    expect(toast.toasts).toHaveLength(0)
  })

  it("traduisent une erreur d'API en message lisible", () => {
    const toast = useToastStore()
    toast.error({ isAxiosError: true, response: { status: 409, data: { detail: 'Déjà pris' } } })
    toast.error({ isAxiosError: true })
    expect(toast.toasts.map((t) => t.message)).toEqual([
      'Déjà pris',
      'Serveur injoignable. Vérifiez votre connexion.',
    ])
  })

  it('exécutent leur action puis se ferment (bouton « Annuler »)', async () => {
    const toast = useToastStore()
    const run = vi.fn()
    toast.success('Archivée', { action: { label: 'Annuler', run } })
    await toast.runAction(toast.toasts[0])
    expect(run).toHaveBeenCalledOnce()
    expect(toast.toasts).toHaveLength(0)
  })
})
