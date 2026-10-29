import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'

vi.mock('../../api/index', () => ({ authApi: { me: vi.fn() } }))

import { authApi } from '../../api/index'
import { createAppRouter } from '../index'
import { makeUser, response } from '../../test/factories'

describe('garde de navigation', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renvoie vers la connexion en gardant la page demandée', async () => {
    vi.mocked(authApi.me).mockRejectedValueOnce(new Error('401'))
    const router = createAppRouter(createMemoryHistory())
    await router.push('/tasks/abc')
    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/tasks/abc')
  })

  it("laisse passer un utilisateur connecté et l'écarte des pages invité", async () => {
    vi.mocked(authApi.me).mockResolvedValueOnce(response(makeUser()) as never)
    const router = createAppRouter(createMemoryHistory())
    await router.push('/relances')
    expect(router.currentRoute.value.name).toBe('follow-up')
    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('home')
  })

  it("laisse un visiteur non connecté voir la vitrine, mais rien d'autre", async () => {
    vi.mocked(authApi.me).mockRejectedValue(new Error('401'))
    const router = createAppRouter(createMemoryHistory())
    await router.push('/projets')
    expect(router.currentRoute.value.name).toBe('public-projects')
    await router.push('/projets/mon-projet')
    expect(router.currentRoute.value.name).toBe('public-project')
    expect(router.currentRoute.value.params.slug).toBe('mon-projet')
    // Les projets privés sont ailleurs, derrière la connexion
    await router.push('/mes-projets')
    expect(router.currentRoute.value.name).toBe('login')
  })
})
