import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('../../api/index', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../../api/index')>()),
  authApi: { login: vi.fn(), register: vi.fn() },
}))

import { authApi } from '../../api/index'
import AuthView from '../AuthView.vue'
import { makeUser, response } from '../../test/factories'

async function mountAt(path: string, props: Record<string, unknown> = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'tasks', component: { template: '<div />' } },
      { path: '/login', name: 'login', component: AuthView },
      { path: '/register', name: 'register', component: AuthView },
      { path: '/tasks/:id', name: 'task', component: { template: '<div />' } },
    ],
  })
  await router.push(path)
  const wrapper = mount(AuthView, { props, global: { plugins: [router] } })
  return { wrapper, router }
}

describe('AuthView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('connecte puis redirige vers la page demandée', async () => {
    vi.mocked(authApi.login).mockResolvedValueOnce(response(makeUser()) as never)
    const { wrapper, router } = await mountAt('/login?redirect=/tasks/42')
    await wrapper.find('#email').setValue('a@example.com')
    await wrapper.find('#password').setValue('secret-password')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(authApi.login).toHaveBeenCalledWith({ email: 'a@example.com', password: 'secret-password' })
    expect(router.currentRoute.value.fullPath).toBe('/tasks/42')
  })

  it("n'accepte pas de redirection vers un autre site", async () => {
    vi.mocked(authApi.login).mockResolvedValueOnce(response(makeUser()) as never)
    const { wrapper, router } = await mountAt('/login?redirect=//evil.example')
    await wrapper.find('#email').setValue('a@example.com')
    await wrapper.find('#password').setValue('secret-password')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/')
  })

  it("affiche l'erreur renvoyée par l'API", async () => {
    vi.mocked(authApi.login).mockRejectedValueOnce({
      isAxiosError: true,
      response: { status: 401, data: { detail: 'Email ou mot de passe incorrect' } },
    })
    const { wrapper } = await mountAt('/login')
    await wrapper.find('#email').setValue('a@example.com')
    await wrapper.find('#password').setValue('wrong')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.find('[role="alert"]').text()).toBe('Email ou mot de passe incorrect')
  })

  it("propose l'inscription avec le champ nom", async () => {
    const { wrapper } = await mountAt('/register', { mode: 'register' })
    expect(wrapper.find('h1').text()).toBe('Créer un compte')
    expect(wrapper.find('#full-name').exists()).toBe(true)
  })
})
