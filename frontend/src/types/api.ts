// Types des réponses de l'API, alignés sur backend/app/schemas.py.
// Les dates sans heure sont des chaînes AAAA-MM-JJ, les horodatages des ISO 8601.

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE'
export type TaskPriority = 'HIGH' | 'MEDIUM' | 'LOW'
export type PresenceStatus = 'PRESENT' | 'LEAVING_SOON' | 'ABSENT' | 'SOON_BACK' | 'RECENTLY_BACK'
export type Recurrence = 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY'
export type FollowUpReason = 'OVERDUE' | 'DUE_TODAY' | 'CLIENT_LEAVING' | 'CLIENT_BACK' | 'WAITING'

/** Date sans heure, au format AAAA-MM-JJ. */
export type IsoDate = string
/** Horodatage ISO 8601. */
export type IsoDateTime = string

export interface User {
  id: string
  email: string
  full_name: string | null
}

export interface RegisterPayload {
  email: string
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
