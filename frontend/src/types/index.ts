export interface User {
  id: number;
  email: string;
  full_name: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
}

export interface Task {
  id: number;
  user_id: number;
  project_id?: number | null;
  title: string;
  description: string;
  priority: 'P1' | 'P2' | 'P3' | 'P4';
  status: 'pendiente' | 'en_progreso' | 'completada' | 'cancelada';
  due_date?: string | null;
  due_time?: string | null;
  estimated_minutes: number;
  is_recurring: boolean;
  recurrence_rule?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  user_id: number;
  name: string;
  slug?: string;
  description: string;
  category: string;
  status: 'activo' | 'pausado' | 'completado' | 'cancelado';
  priority: 'P1' | 'P2' | 'P3' | 'P4';
  target_date?: string | null;
  created_at: string;
  updated_at: string;
  total_tasks?: number;
  completed_tasks?: number;
  progress_percentage?: number;
}

export interface Note {
  id: number;
  user_id: number;
  project_id?: number | null;
  title: string;
  content: string;
  category: 'idea' | 'nota' | 'recurso' | 'referencia';
  tags: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface EventItem {
  id: number;
  user_id: number;
  project_id?: number | null;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  location: string;
  is_all_day: boolean;
  created_at: string;
}

export interface FinanceRecord {
  id: number;
  user_id: number;
  type: 'ingreso' | 'gasto';
  category: string;
  amount: number;
  currency: string;
  description: string;
  date: string;
  created_at: string;
}

export interface FinanceSummary {
  total_income: number;
  total_expense: number;
  net_balance: number;
  by_category: Record<string, number>;
  currency: string;
}

export interface Memory {
  id: number;
  user_id: number;
  level: 'permanent' | 'operational' | 'historical';
  category: string;
  key: string;
  value: string;
  confidence: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: string | null;
  tool_results?: string | null;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
  last_message?: string | null;
}

export interface DashboardSummary {
  user_name: string;
  date: string;
  workload_hours: number;
  is_overloaded: boolean;
  metrics: {
    overdue_tasks_count: number;
    today_tasks_count: number;
    total_pending_tasks: number;
    completed_today: number;
    active_projects: number;
    month_income: number;
    month_expense: number;
    month_balance: number;
  };
  overdue_tasks: Array<{ id: number; title: string; priority: string; due_date?: string }>;
  today_tasks: Array<{ id: number; title: string; priority: string; estimated_minutes: number }>;
  upcoming_events: Array<{ id: number; title: string; start_time: string; location: string }>;
  key_memories: Array<{ key: string; value: string; category: string }>;
}
