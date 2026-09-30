// Données de test complètes et typées : chaque test ne précise que ce qui le concerne.
import type { Client, Company, TaskLog, TaskSummary, User } from '../types/api'

export function makeCompany(overrides: Partial<Company> = {}): Company {
  return { id: 'company-1', name: 'Atelier Boréal', archived_at: null, ...overrides }
}

export function makeClient(overrides: Partial<Client> = {}): Client {
  return {
    id: 'client-1',
    company_id: 'company-1',
    first_name: 'Camille',
    last_name: 'Durand',
    email: null,
    absence_start_date: null,
    absence_end_date: null,
    archived_at: null,
    company: makeCompany(),
    presence_status: 'PRESENT',
    ...overrides,
  }
}

export function makeTask(overrides: Partial<TaskSummary> = {}): TaskSummary {
  const id = overrides.id ?? 'task-1'
  return {
    id,
    client_id: 'client-1',
    title: id,
    description: null,
    status: 'TODO',
    sub_status: null,
    priority: 'MEDIUM',
    due_date: null,
    created_at: '2026-09-01T09:00:00Z',
    updated_at: '2026-09-01T09:00:00Z',
    archived_at: null,
    client: makeClient(),
    comments_count: 0,
    ...overrides,
  }
}

export function makeLog(overrides: Partial<TaskLog> = {}): TaskLog {
  return {
    id: 'log-1',
    task_id: 'task-1',
    field_changed: 'status',
    old_value: null,
    new_value: null,
    old_label: null,
    new_label: null,
    comment: null,
    created_at: '2026-09-01T09:00:00Z',
    ...overrides,
  }
}

export function makeUser(overrides: Partial<User> = {}): User {
  return { id: 'user-1', email: 'a@example.com', full_name: null, ...overrides }
}

/** Réponse axios minimale pour les mocks. */
export function response<T>(data: T) {
  return { data }
}
