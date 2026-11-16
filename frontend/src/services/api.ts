import axios from 'axios';
import type {
  User,
  Task,
  Project,
  Note,
  EventItem,
  FinanceRecord,
  FinanceSummary,
  Memory,
  Conversation,
  Message,
  DashboardSummary
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para inyectar token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('nexus_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar expiración de sesión
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('nexus_token');
      localStorage.removeItem('nexus_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Autenticación
  auth: {
    login: async (email: string, password: string) => {
      const resp = await api.post('/auth/login', { email, password });
      return resp.data;
    },
    register: async (email: string, password: string, fullName: string) => {
      const resp = await api.post('/auth/register', { email, password, full_name: fullName });
      return resp.data;
    },
    getMe: async (): Promise<User> => {
      const resp = await api.get('/auth/me');
      return resp.data;
    }
  },

  // Dashboard
  dashboard: {
    getSummary: async (): Promise<DashboardSummary> => {
      const resp = await api.get('/dashboard/summary');
      return resp.data;
    }
  },

  // Asistente / Chat
  chat: {
    getConversations: async (): Promise<Conversation[]> => {
      const resp = await api.get('/chat/conversations');
      return resp.data;
    },
    getConversation: async (id: number): Promise<Conversation & { messages: Message[] }> => {
      const resp = await api.get(`/chat/conversations/${id}`);
      return resp.data;
    },
    createConversation: async (title: string): Promise<Conversation> => {
      const resp = await api.post(`/chat/conversations?title=${encodeURIComponent(title)}`);
      return resp.data;
    },
    sendMessage: async (message: string, conversationId?: number): Promise<Message> => {
      const resp = await api.post('/chat/send', {
        message,
        conversation_id: conversationId
      });
      return resp.data;
    }
  },

  // Tareas
  tasks: {
    list: async (filters?: { status?: string; priority?: string; projectId?: number; dueDate?: string }): Promise<Task[]> => {
      const resp = await api.get('/tasks/', { params: filters });
      return resp.data;
    },
    create: async (data: Partial<Task>): Promise<Task> => {
      const resp = await api.post('/tasks/', data);
      return resp.data;
    },
    update: async (id: number, data: Partial<Task>): Promise<Task> => {
      const resp = await api.put(`/tasks/${id}`, data);
      return resp.data;
    },
    toggleComplete: async (id: number): Promise<Task> => {
      const resp = await api.post(`/tasks/${id}/complete`);
      return resp.data;
    },
    delete: async (id: number): Promise<void> => {
      await api.delete(`/tasks/${id}`);
    }
  },

  // Proyectos
  projects: {
    list: async (status?: string): Promise<Project[]> => {
      const resp = await api.get('/projects/', { params: { status } });
      return resp.data;
    },
    create: async (data: Partial<Project>): Promise<Project> => {
      const resp = await api.post('/projects/', data);
      return resp.data;
    },
    update: async (id: number, data: Partial<Project>): Promise<Project> => {
      const resp = await api.put(`/projects/${id}`, data);
      return resp.data;
    },
    delete: async (id: number): Promise<void> => {
      await api.delete(`/projects/${id}`);
    }
  },

  // Agenda / Eventos
  events: {
    list: async (start?: string, end?: string): Promise<EventItem[]> => {
      const resp = await api.get('/events/', { params: { start, end } });
      return resp.data;
    },
    create: async (data: Partial<EventItem>): Promise<EventItem> => {
      const resp = await api.post('/events/', data);
      return resp.data;
    },
    update: async (id: number, data: Partial<EventItem>): Promise<EventItem> => {
      const resp = await api.put(`/events/${id}`, data);
      return resp.data;
    },
    delete: async (id: number): Promise<void> => {
      await api.delete(`/events/${id}`);
    }
  },

  // Notas
  notes: {
    list: async (category?: string, search?: string): Promise<Note[]> => {
      const resp = await api.get('/notes/', { params: { category, search } });
      return resp.data;
    },
    create: async (data: Partial<Note>): Promise<Note> => {
      const resp = await api.post('/notes/', data);
      return resp.data;
    },
    update: async (id: number, data: Partial<Note>): Promise<Note> => {
      const resp = await api.put(`/notes/${id}`, data);
      return resp.data;
    },
    delete: async (id: number): Promise<void> => {
      await api.delete(`/notes/${id}`);
    }
  },

  // Finanzas
  finances: {
    list: async (type?: string, month?: string): Promise<FinanceRecord[]> => {
      const resp = await api.get('/finances/', { params: { type, month } });
      return resp.data;
    },
    getSummary: async (month?: string): Promise<FinanceSummary> => {
      const resp = await api.get('/finances/summary', { params: { month } });
      return resp.data;
    },
    create: async (data: Partial<FinanceRecord>): Promise<FinanceRecord> => {
      const resp = await api.post('/finances/', data);
      return resp.data;
    },
    delete: async (id: number): Promise<void> => {
      await api.delete(`/finances/${id}`);
    }
  },

  // Memoria persistente
  memories: {
    list: async (level?: string, category?: string): Promise<Memory[]> => {
      const resp = await api.get('/memories/', { params: { level, category } });
      return resp.data;
    },
    create: async (data: Partial<Memory>): Promise<Memory> => {
      const resp = await api.post('/memories/', data);
      return resp.data;
    },
    update: async (id: number, data: Partial<Memory>): Promise<Memory> => {
      const resp = await api.put(`/memories/${id}`, data);
      return resp.data;
    },
    delete: async (id: number): Promise<void> => {
      await api.delete(`/memories/${id}`);
    }
  }
};
