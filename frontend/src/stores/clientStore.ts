import { defineStore } from 'pinia'
import { ref } from 'vue'
import { clientsApi, companiesApi } from '../api/index'
import { fullName, presenceColor, presenceLabel } from '../utils/labels'
import type { Client, ClientPayload, Company } from '../types/api'

const byName = (a: Company, b: Company) => a.name.localeCompare(b.name)

export const useClientStore = defineStore('clients', () => {
  const clients = ref<Client[]>([])
  const companies = ref<Company[]>([])
  const loading = ref(false)

  async function fetchClients() {
    loading.value = true
    try {
      clients.value = (await clientsApi.getAll()).data
    } finally {
      loading.value = false
    }
  }

  async function fetchCompanies() {
    companies.value = (await companiesApi.getAll()).data
  }

  async function fetchAll() {
    await Promise.all([fetchClients(), fetchCompanies()])
  }

  async function createCompany(name: string) {
    const company = (await companiesApi.create({ name })).data
    companies.value = [...companies.value, company].sort(byName)
    return company
  }

  async function createClient(data: ClientPayload) {
    const client = (await clientsApi.create(data)).data
    clients.value.push(client)
    return client
  }

  async function updateClient(id: string, data: ClientPayload) {
    const client = (await clientsApi.update(id, data)).data
    const idx = clients.value.findIndex((c) => c.id === id)
    if (idx !== -1) clients.value[idx] = client
    return client
  }

  async function editCompany(id: string, name: string) {
    const company = (await companiesApi.update(id, { name })).data
    const idx = companies.value.findIndex((c) => c.id === id)
    if (idx !== -1) companies.value[idx] = company
    // Le nom de l'entreprise est embarqué dans chaque client
    clients.value = clients.value.map((c) => (c.company_id === id ? { ...c, company } : c))
    return company
  }

  // Archiver est réversible : restore* réactive ce qui a été archivé ensemble.
  async function archiveClient(id: string) {
    await clientsApi.archive(id)
    clients.value = clients.value.filter((c) => c.id !== id)
  }

  async function restoreClient(id: string) {
    await clientsApi.restore(id)
    await fetchClients()
  }

  async function archiveCompany(id: string) {
    await companiesApi.archive(id)
    companies.value = companies.value.filter((c) => c.id !== id)
    clients.value = clients.value.filter((c) => c.company_id !== id)
  }

  async function restoreCompany(id: string) {
    await companiesApi.restore(id)
    await fetchAll()
  }

  function reset() {
    clients.value = []
    companies.value = []
  }

  return {
    clients,
    companies,
    loading,
    fetchClients,
    fetchCompanies,
    fetchAll,
    createCompany,
    createClient,
    updateClient,
    editCompany,
    archiveClient,
    restoreClient,
    archiveCompany,
    restoreCompany,
    reset,
    // Aides d'affichage, conservées ici pour les composants existants
    presenceColor,
    presenceLabel,
    fullName,
  }
})
