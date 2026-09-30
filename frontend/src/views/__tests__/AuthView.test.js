import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('../../api/index.js', async (importOriginal) => ({
  ...(await importOriginal()),
  authApi: { login: vi.fn(), register: vi.fn() },
}))

import { authApi } from '../../api/index.js'
import AuthView from '../AuthView.vue'

async function mountAt(path, props = {}) {
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
    authApi.login.mockResolvedValueOnce({ data: { id: '1', email: 'a@example.com' } })
    const { wrapper, router } = await mountAt('/login?redirect=/tasks/42')
    await wrapper.find('#email').setValue('a@example.com')
    await wrapper.find('#password').setValue('secret-password')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(authApi.login).toHaveBeenCalledWith({ email: 'a@example.com', password: 'secret-password' })
    expect(router.currentRoute.value.fullPath).toBe('/tasks/42')
  })

  it("n'accepte pas de redirection vers un autre site", async () => {
    authApi.login.mockResolvedValueOnce({ data: { id: '1', email: 'a@example.com' } })
    const { wrapper, router } = await mountAt('/login?redirect=//evil.example')
    await wrapper.find('#email').setValue('a@example.com')
    await wrapper.find('#password').setValue('secret-password')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/')
  })

  it("affiche l'erreur renvoyée par l'API", async () => {
    authApi.login.mockRejectedValueOnce({
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
