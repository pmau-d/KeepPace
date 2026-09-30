import { defineStore } from 'pinia'
import { ref } from 'vue'
import { clientsApi, companiesApi, adminApi } from '../api/index.js'

export const useClientStore = defineStore('clients', () => {
  const clients = ref([])
  const companies = ref([])
  const loading = ref(false)

  async function fetchClients() {
    loading.value = true
    try {
      const res = await clientsApi.getAll()
      clients.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchCompanies() {
    const res = await companiesApi.getAll()
    companies.value = res.data
  }

  async function createCompany(name) {
    const res = await companiesApi.create({ name })
    companies.value.push(res.data)
    companies.value.sort((a, b) => a.name.localeCompare(b.name))
    return res.data
  }

  async function createClient(data) {
    const res = await clientsApi.create(data)
    clients.value.push(res.data)
    return res.data
  }

  async function updateClient(id, data) {
    const res = await clientsApi.update(id, data)
    const idx = clients.value.findIndex((c) => c.id === id)
    if (idx !== -1) clients.value[idx] = res.data
    return res.data
  }

  async function deleteClient(id) {
    await clientsApi.delete(id)
    clients.value = clients.value.filter((c) => c.id !== id)
  }

  async function deleteCompany(id) {
    await companiesApi.delete(id)
    companies.value = companies.value.filter((c) => c.id !== id)
    clients.value = clients.value.filter((c) => c.company_id !== id)
  }

  async function editCompany(id, name) {
    const res = await companiesApi.update(id, { name })
    const idx = companies.value.findIndex((c) => c.id === id)
    if (idx !== -1) companies.value[idx] = res.data
    // Rafraîchir les clients (leur company.name est embarqué)
    clients.value = clients.value.map((c) =>
      c.company_id === id ? { ...c, company: res.data } : c,
    )
    return res.data
  }

  async function resetAll() {
    await adminApi.reset()
    clients.value = []
    companies.value = []
  }

  // ─── Helpers ───────────────────────────────────────────────────────────────

  function presenceColor(status) {
    return (
      {
        PRESENT: 'bg-green-500',
        ABSENT: 'bg-red-500',
        SOON_BACK: 'bg-yellow-400',
        RECENTLY_BACK: 'bg-blue-500',
      }[status] ?? 'bg-slate-400'
    )
  }

  function presenceLabel(status) {
    return (
      {
        PRESENT: '🟢 Présent',
        ABSENT: '🔴 Absent',
        SOON_BACK: '🟡 Bientôt de retour',
        RECENTLY_BACK: '🔵 Rentré récemment',
      }[status] ?? 'Inconnu'
    )
  }

  /** Retourne "Prénom Nom" ou juste "Prénom" si pas de nom */
  function fullName(client) {
    if (!client) return ''
    return [client.first_name, client.last_name].filter(Boolean).join(' ')
  }

  return {
    clients, companies, loading,
    fetchClients, fetchCompanies,
    createCompany, createClient,
    updateClient, editCompany,
    deleteClient, deleteCompany, resetAll,
    presenceColor, presenceLabel, fullName,
  }
})

