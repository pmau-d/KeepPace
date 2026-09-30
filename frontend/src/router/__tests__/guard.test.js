import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'

vi.mock('../../api/index.js', () => ({ authApi: { me: vi.fn() } }))

import { authApi } from '../../api/index.js'
import { createAppRouter } from '../index.js'

describe('garde de navigation', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renvoie vers la connexion en gardant la page demandée', async () => {
    authApi.me.mockRejectedValueOnce(new Error('401'))
    const router = createAppRouter(createMemoryHistory())
    await router.push('/tasks/abc')
    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/tasks/abc')
  })

  it("laisse passer un utilisateur connecté et l'écarte des pages invité", async () => {
    authApi.me.mockResolvedValueOnce({ data: { id: '1', email: 'a@example.com' } })
    const router = createAppRouter(createMemoryHistory())
    await router.push('/relances')
    expect(router.currentRoute.value.name).toBe('follow-up')
    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('tasks')
  })
})
