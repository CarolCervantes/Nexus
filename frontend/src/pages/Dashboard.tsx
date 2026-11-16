import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  CheckSquare,
  AlertTriangle,
  FolderKanban,
  Calendar,
  DollarSign,
  Bot,
  ArrowRight,
  Clock,
  Sparkles,
  Brain
} from 'lucide-react';
import { apiService } from '../services/api';
import type { DashboardSummary } from '../types';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchSummary = async () => {
    try {
      const summary = await apiService.dashboard.getSummary();
      setData(summary);
    } catch (err) {
      console.error('Error al cargar dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const handleToggleTask = async (taskId: number) => {
    try {
      await apiService.tasks.toggleComplete(taskId);
      fetchSummary();
    } catch (err) {
      console.error('Error al completar tarea:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Buenos días' : hour < 19 ? 'Buenas tardes' : 'Buenas noches';

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Hero Welcome & Quick Chat Prompt */}
      <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 p-6 md:p-8 overflow-hidden shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-medium mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>NEXUS conectado • Sincronización en la nube</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
              {greeting}, {data?.user_name}
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Tienes <span className="text-cyan-400 font-semibold">{data?.metrics.total_pending_tasks} tareas pendientes</span> y{' '}
              <span className="text-indigo-400 font-semibold">{data?.metrics.active_projects} proyectos activos</span> en seguimiento.
            </p>
          </div>

          <Link
            to="/chat"
            className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-medium text-sm shadow-lg shadow-cyan-500/20 hover:opacity-95 active:scale-95 transition-all shrink-0"
          >
            <Bot className="w-4 h-4" />
            <span>Hablar con NEXUS</span>
          </Link>
        </div>
      </div>

      {/* Overload or Overdue Alert */}
      {data?.metrics.overdue_tasks_count! > 0 && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
          <div className="flex-1 text-sm">
            <p className="font-semibold">Atención: Tienes {data?.metrics.overdue_tasks_count} tarea(s) vencida(s)</p>
            <p className="text-xs text-rose-400/90 mt-0.5">
              Revisa tus pendientes críticos de inmediato para evitar atrasos en tus entregables.
            </p>
          </div>
          <Link to="/tasks" className="text-xs font-semibold underline hover:text-white shrink-0">
            Ver tareas
          </Link>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Tareas Pendientes</span>
            <CheckSquare className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-white">{data?.metrics.total_pending_tasks}</p>
          <span className="text-[11px] text-slate-500">{data?.metrics.completed_today} completadas hoy</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Carga Estimada Hoy</span>
            <Clock className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-white">{data?.workload_hours}h</p>
          <span className={`text-[11px] ${data?.is_overloaded ? 'text-rose-400' : 'text-emerald-400'}`}>
            {data?.is_overloaded ? 'Sobrecarga (>7h)' : 'Carga balanceada'}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Proyectos Activos</span>
            <FolderKanban className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-white">{data?.metrics.active_projects}</p>
          <Link to="/projects" className="text-[11px] text-cyan-400 hover:underline">Ver proyectos</Link>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Balance del Mes</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-white">
            ${data?.metrics.month_balance?.toLocaleString()}
          </p>
          <span className="text-[11px] text-slate-500">COP</span>
        </div>
      </div>

      {/* Main Grid: Today's Tasks & Agenda */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Tareas de Hoy / Vencidas (2 Cols) */}
        <div className="md:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-cyan-400" />
              <span>Tareas Recomendadas para Hoy</span>
            </h2>
            <Link to="/tasks" className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
              <span>Gestionar todas</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl divide-y divide-slate-800/80 overflow-hidden shadow-sm">
            {(!data?.today_tasks.length && !data?.overdue_tasks.length) ? (
              <div className="p-8 text-center text-slate-500 text-sm">
                No tienes tareas pendientes programadas para hoy. ¡Estás al día!
              </div>
            ) : (
              <>
                {/* Overdue */}
                {data?.overdue_tasks.map((task) => (
                  <div key={task.id} className="p-3.5 flex items-center justify-between gap-3 bg-rose-500/5 hover:bg-rose-500/10 transition-colors">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleToggleTask(task.id)}
                        className="w-5 h-5 rounded-md border border-rose-400/40 hover:bg-rose-500/20 flex items-center justify-center transition-colors"
                      />
                      <div>
                        <p className="text-sm font-medium text-slate-200">{task.title}</p>
                        <span className="text-[10px] text-rose-400 font-medium">Venció: {task.due_date}</span>
                      </div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-bold">
                      {task.priority}
                    </span>
                  </div>
                ))}

                {/* Today */}
                {data?.today_tasks.map((task) => (
                  <div key={task.id} className="p-3.5 flex items-center justify-between gap-3 hover:bg-slate-800/40 transition-colors">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleToggleTask(task.id)}
                        className="w-5 h-5 rounded-md border border-slate-600 hover:border-cyan-400 hover:bg-cyan-500/20 flex items-center justify-center transition-colors"
                      />
                      <div>
                        <p className="text-sm font-medium text-slate-200">{task.title}</p>
                        <span className="text-[10px] text-slate-400 font-mono">~{task.estimated_minutes} min</span>
                      </div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
                      {task.priority}
                    </span>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>

        {/* Side Column: Agenda & Memories */}
        <div className="space-y-6">
          {/* Upcoming Events */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Calendar className="w-4 h-4 text-indigo-400" />
                <span>Próximos Eventos</span>
              </h2>
              <Link to="/calendar" className="text-xs text-indigo-400 hover:underline">Ver agenda</Link>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-3">
              {!data?.upcoming_events.length ? (
                <p className="text-xs text-slate-500 text-center py-4">Sin eventos programados para los próximos días.</p>
              ) : (
                data.upcoming_events.map((ev) => (
                  <div key={ev.id} className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-800/80">
                    <p className="text-xs font-semibold text-slate-200">{ev.title}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">
                      {new Date(ev.start_time).toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' })}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Key Memories */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Brain className="w-4 h-4 text-cyan-400" />
                <span>Memoria del Asistente</span>
              </h2>
              <Link to="/memories" className="text-xs text-cyan-400 hover:underline">Gestionar</Link>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
              {!data?.key_memories.length ? (
                <p className="text-xs text-slate-500 text-center py-2">Sin recuerdos permanentes configurados.</p>
              ) : (
                data.key_memories.map((m, idx) => (
                  <div key={idx} className="text-xs text-slate-300 flex items-center justify-between py-1 border-b border-slate-800/50 last:border-0">
                    <span className="font-mono text-cyan-400">{m.key}</span>
                    <span className="text-slate-400 text-right truncate max-w-[150px]">{m.value}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
