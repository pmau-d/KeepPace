// Types des réponses de l'API, alignés sur backend/app/schemas.py.
// Les dates sans heure sont des chaînes AAAA-MM-JJ, les horodatages des ISO 8601.

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE'
export type TaskPriority = 'HIGH' | 'MEDIUM' | 'LOW'
export type PresenceStatus = 'PRESENT' | 'LEAVING_SOON' | 'ABSENT' | 'SOON_BACK' | 'RECENTLY_BACK'
export type ProjectStatus = 'IDEA' | 'ACTIVE' | 'PAUSED' | 'DELIVERED'
/** Nature d'une tâche de projet. */
export type TaskKind = 'TASK' | 'BUG' | 'IMPROVEMENT'
export type Recurrence = 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY'
export type FollowUpReason = 'OVERDUE' | 'DUE_TODAY' | 'CLIENT_LEAVING' | 'CLIENT_BACK' | 'WAITING'

/** Date sans heure, au format AAAA-MM-JJ. */
export type IsoDate = string
/** Horodatage ISO 8601. */
export type IsoDateTime = string

export interface User {
  id: string
  /** Identifiant de connexion, en minuscules. */
  username: string
  /** Facultatif : sert au récap quotidien par email. */
  email: string | null
  full_name: string | null
  digest_opt_in: boolean
}

export interface DigestClient {
  id: string
  name: string
  on: IsoDate | null
}

export interface Digest {
  day: IsoDate
  follow_up_total: number
  counts: Partial<Record<FollowUpReason, number>>
  leaving: DigestClient[]
  returning: DigestClient[]
  /** Le serveur sait envoyer des emails (DIGEST_ENABLED et SMTP). */
  email_available: boolean
}

export interface RegisterPayload {
  username: string
  password: string
  full_name: string | null
}

export interface Company {
  id: string
  name: string
  archived_at: IsoDateTime | null
}

export interface Client {
  id: string
  company_id: string
  first_name: string
  last_name: string | null
  email: string | null
  absence_start_date: IsoDate | null
  absence_end_date: IsoDate | null
  archived_at: IsoDateTime | null
  company: Company
  presence_status: PresenceStatus | null
  /** Tâches ni terminées ni archivées. */
  open_tasks_count: number
}

export interface ClientPayload {
  company_id?: string
  first_name?: string
  last_name?: string | null
  email?: string | null
  absence_start_date?: IsoDate | null
  absence_end_date?: IsoDate | null
}

export interface TaskComment {
  id: string
  task_id: string
  content: string
  created_at: IsoDateTime
}

export interface TaskLog {
  id: string
  task_id: string
  field_changed: string
  old_value: string | null
  new_value: string | null
  old_label: string | null
  new_label: string | null
  comment: string | null
  created_at: IsoDateTime
}

export interface TaskSummary {
  id: string
  client_id: string
  title: string
  description: string | null
  status: TaskStatus
  sub_status: string | null
  priority: TaskPriority
  due_date: IsoDate | null
  /** null : tâche ponctuelle. */
  recurrence: Recurrence | null
  recurrence_interval: number
  created_at: IsoDateTime
  updated_at: IsoDateTime
  archived_at: IsoDateTime | null
  client: Client
  comments_count: number
}

export interface Task extends TaskSummary {
  comments: TaskComment[]
}

export interface TaskPage {
  items: TaskSummary[]
  total: number
  limit: number
  offset: number
}

export interface FollowUpItem extends TaskSummary {
  follow_up_reason: FollowUpReason
}

export interface TaskCreatePayload {
  client_id: string
  title: string
  description?: string | null
  status?: TaskStatus
  sub_status?: string | null
  priority?: TaskPriority
  due_date?: IsoDate | null
  recurrence?: Recurrence | null
  recurrence_interval?: number
}

export interface TaskUpdatePayload {
  title?: string
  description?: string | null
  client_id?: string
  status?: TaskStatus
  sub_status?: string | null
  priority?: TaskPriority
  due_date?: IsoDate | null
  recurrence?: Recurrence | null
  recurrence_interval?: number
  /** Note enregistrée dans l'historique, pas dans la tâche. */
  comment?: string
}

/** Paramètres de filtre acceptés par GET /tasks/ et l'export CSV. */
export interface TaskQuery {
  client_id?: string
  status?: TaskStatus
  presence_status?: PresenceStatus
  show_done?: boolean
  search?: string
  archived?: boolean
  limit?: number
  offset?: number
}

export interface Project {
  id: string
  name: string
  /** Adresse stable du projet (/projets/<slug> pour la vitrine publique). */
  slug: string
  description: string | null
  status: ProjectStatus
  /** Visible sans connexion sur /projets/<slug>. */
  is_public: boolean
  created_at: IsoDateTime
  archived_at: IsoDateTime | null
  tasks_total: number
  tasks_done: number
  /** Pourcentage de tâches terminées, 0 à 100. */
  progress: number
}

export interface ProjectPayload {
  name?: string
  description?: string | null
  status?: ProjectStatus
  is_public?: boolean
}

/** Vitrine publique : ce que voit un visiteur non connecté, rien de plus. */
export interface PublicProjectCard {
  name: string
  slug: string
  description: string | null
  status: ProjectStatus
  progress: number
}

export interface PublicProject extends PublicProjectCard {
  completed_tasks: { title: string; completed_at: IsoDateTime }[]
}

export interface ProjectTask {
  id: string
  project_id: string
  kind: TaskKind
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  due_date: IsoDate | null
  recurrence: Recurrence | null
  recurrence_interval: number
  created_at: IsoDateTime
  updated_at: IsoDateTime
}

export interface ProjectTaskCreatePayload {
  project_id: string
  title: string
  kind?: TaskKind
  description?: string | null
  status?: TaskStatus
  priority?: TaskPriority
  due_date?: IsoDate | null
  recurrence?: Recurrence | null
  recurrence_interval?: number
}

export type ProjectTaskUpdatePayload = Partial<Omit<ProjectTaskCreatePayload, 'project_id'>>
