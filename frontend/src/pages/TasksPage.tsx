import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Plus,
  Trash2,
  Calendar,
  Clock,
  Filter,
  CheckCircle2,
  Circle,
  X
} from 'lucide-react';
import { apiService } from '../services/api';
import type { Task, Project } from '../types';

export const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('pendiente');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [showModal, setShowModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'P1' | 'P2' | 'P3' | 'P4'>('P3');
  const [dueDate, setDueDate] = useState('');
  const [estimatedMinutes, setEstimatedMinutes] = useState(30);
  const [projectId, setProjectId] = useState<number | undefined>(undefined);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const data = await apiService.tasks.list({
        status: statusFilter || undefined,
        priority: priorityFilter || undefined
      });
      setTasks(data);
    } catch (err) {
      console.error('Error al cargar tareas:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const data = await apiService.projects.list('activo');
      setProjects(data);
    } catch (err) {
      console.error('Error al cargar proyectos:', err);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [statusFilter, priorityFilter]);

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleToggleComplete = async (id: number) => {
    try {
      await apiService.tasks.toggleComplete(id);
      fetchTasks();
    } catch (err) {
      console.error('Error al cambiar estado:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Seguro que deseas eliminar esta tarea?')) return;
    try {
      await apiService.tasks.delete(id);
      fetchTasks();
    } catch (err) {
      console.error('Error al eliminar tarea:', err);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      await apiService.tasks.create({
        title,
        description,
        priority,
        due_date: dueDate || null,
        estimated_minutes: estimatedMinutes,
        project_id: projectId || null,
        status: 'pendiente'
      });
      setShowModal(false);
      setTitle('');
      setDescription('');
      setPriority('P3');
      setDueDate('');
      setEstimatedMinutes(30);
      setProjectId(undefined);
      fetchTasks();
    } catch (err) {
      console.error('Error al crear tarea:', err);
    }
  };

  const getPriorityBadge = (prio: string) => {
    switch (prio) {
      case 'P1':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'P2':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'P3':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <CheckSquare className="w-6 h-6 text-cyan-400" />
            <span>Gestión de Tareas</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Organiza, prioriza y controla tus actividades diarias y académicas.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-medium text-xs shadow-md shadow-cyan-500/20 hover:opacity-95 active:scale-95 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Nueva Tarea</span>
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center gap-2 bg-slate-900/60 p-2 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div className="flex items-center gap-1.5 px-2 text-xs text-slate-400">
          <Filter className="w-3.5 h-3.5" />
          <span>Estado:</span>
        </div>
        {['pendiente', 'completada', ''].map((st) => (
          <button
            key={st}
            onClick={() => setStatusFilter(st)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              statusFilter === st
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
            }`}
          >
            {st === 'pendiente' ? 'Pendientes' : st === 'completada' ? 'Completadas' : 'Todas'}
          </button>
        ))}

        <div className="h-4 w-[1px] bg-slate-800 mx-1" />

        <div className="flex items-center gap-1">
          {['', 'P1', 'P2', 'P3'].map((p) => (
            <button
              key={p}
              onClick={() => setPriorityFilter(p)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                priorityFilter === p
                  ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {p || 'Prio: Todas'}
            </button>
          ))}
        </div>
      </div>

      {/* Tasks List */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden divide-y divide-slate-800/60 backdrop-blur-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Cargando tareas...</div>
        ) : tasks.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            No hay tareas que coincidan con los filtros seleccionados.
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="p-4 flex items-center justify-between gap-3 hover:bg-slate-800/30 transition-colors"
            >
              <div className="flex items-start gap-3.5 flex-1 min-w-0">
                <button
                  onClick={() => handleToggleComplete(task.id)}
                  className="mt-0.5 text-slate-500 hover:text-cyan-400 transition-colors shrink-0"
                >
                  {task.status === 'completada' ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <Circle className="w-5 h-5 text-slate-500 hover:text-cyan-400" />
                  )}
                </button>

                <div className="min-w-0 flex-1">
                  <p
                    className={`text-sm font-medium truncate ${
                      task.status === 'completada' ? 'line-through text-slate-500' : 'text-slate-100'
                    }`}
                  >
                    {task.title}
                  </p>
                  {task.description && (
                    <p className="text-xs text-slate-400 line-clamp-1 mt-0.5">{task.description}</p>
                  )}
                  <div className="flex flex-wrap items-center gap-3 mt-1.5 text-[11px] text-slate-400">
                    {task.due_date && (
                      <span className="flex items-center gap-1 font-mono">
                        <Calendar className="w-3 h-3 text-cyan-400" />
                        <span>{task.due_date}</span>
                      </span>
                    )}
                    <span className="flex items-center gap-1 font-mono">
                      <Clock className="w-3 h-3 text-indigo-400" />
                      <span>~{task.estimated_minutes} min</span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <span
                  className={`text-[10px] px-2.5 py-0.5 rounded-full border font-bold ${getPriorityBadge(
                    task.priority
                  )}`}
                >
                  {task.priority}
                </span>

                <button
                  onClick={() => handleDelete(task.id)}
                  className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                  title="Eliminar tarea"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal Nueva Tarea */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Crear Nueva Tarea</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-300 mb-1">Título *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ej. Revisar avance con profesor"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Descripción</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Detalles adicionales..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Prioridad</label>
                  <select
                    value={priority}
                    onChange={(e: any) => setPriority(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  >
                    <option value="P1">🚨 P1 - Urgente e Importante</option>
                    <option value="P2">⏳ P2 - Importante</option>
                    <option value="P3">📌 P3 - Normal</option>
                    <option value="P4">💤 P4 - Baja</option>
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-slate-300 mb-1">Proyecto</label>
                  <select
                    value={projectId || ''}
                    onChange={(e) => setProjectId(e.target.value ? Number(e.target.value) : undefined)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  >
                    <option value="">(Ninguno)</option>
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Fecha Límite</label>
                  <input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  />
                </div>

                <div>
                  <label className="block font-medium text-slate-300 mb-1">Tiempo Estimado (min)</label>
                  <input
                    type="number"
                    value={estimatedMinutes}
                    onChange={(e) => setEstimatedMinutes(Number(e.target.value))}
                    min={5}
                    step={5}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-medium shadow-md shadow-cyan-500/20"
                >
                  Guardar Tarea
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
