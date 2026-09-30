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
    expect(router.currentRoute.value.name).toBe('tasks')
  })
})
