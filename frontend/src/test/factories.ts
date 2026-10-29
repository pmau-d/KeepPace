// Données de test complètes et typées : chaque test ne précise que ce qui le concerne.
import type { Client, Company, Project, ProjectTask, TaskLog, TaskSummary, User } from '../types/api'

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
    open_tasks_count: 0,
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
    recurrence: null,
    recurrence_interval: 1,
    created_at: '2026-09-01T09:00:00Z',
    updated_at: '2026-09-01T09:00:00Z',
    archived_at: null,
    checklist_total: 0,
    checklist_done: 0,
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
  return {
    id: 'user-1',
    username: 'alice',
    email: null,
    full_name: null,
    digest_opt_in: false,
    ...overrides,
  }
}

/** Réponse axios minimale pour les mocks. */
export function response<T>(data: T) {
  return { data }
}

export function makeProject(overrides: Partial<Project> = {}): Project {
  return {
    id: 'project-1',
    name: 'Site vitrine',
    slug: 'site-vitrine',
    description: null,
    status: 'ACTIVE',
    is_public: false,
    created_at: '2026-09-01T09:00:00Z',
    archived_at: null,
    tasks_total: 0,
    tasks_done: 0,
    progress: 0,
    ...overrides,
  }
}

export function makeProjectTask(overrides: Partial<ProjectTask> = {}): ProjectTask {
  const id = overrides.id ?? 'ptask-1'
  return {
    id,
    project_id: 'project-1',
    kind: 'TASK',
    title: id,
    description: null,
    status: 'TODO',
    priority: 'MEDIUM',
    due_date: null,
    recurrence: null,
    recurrence_interval: 1,
    created_at: '2026-09-01T09:00:00Z',
    updated_at: '2026-09-01T09:00:00Z',
    checklist: [],
    ...overrides,
  }
}
