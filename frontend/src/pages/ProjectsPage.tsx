import React, { useState, useEffect } from 'react';
import { FolderKanban, Plus, Target, CheckCircle2, X } from 'lucide-react';
import { apiService } from '../services/api';
import type { Project } from '../types';

export const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('personal');
  const [priority, setPriority] = useState<'P1' | 'P2' | 'P3' | 'P4'>('P3');
  const [targetDate, setTargetDate] = useState('');

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await apiService.projects.list();
      setProjects(data);
    } catch (err) {
      console.error('Error al cargar proyectos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      await apiService.projects.create({
        name,
        description,
        category,
        priority,
        target_date: targetDate || null,
        status: 'activo'
      });
      setShowModal(false);
      setName('');
      setDescription('');
      setCategory('personal');
      setPriority('P3');
      setTargetDate('');
      fetchProjects();
    } catch (err) {
      console.error('Error al crear proyecto:', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <FolderKanban className="w-6 h-6 text-indigo-400" />
            <span>Proyectos</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Supervisa el avance y métricas de tus iniciativas personales y académicas.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-medium text-xs shadow-md shadow-cyan-500/20 hover:opacity-95 active:scale-95 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Nuevo Proyecto</span>
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 text-sm">Cargando proyectos...</div>
      ) : projects.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-sm bg-slate-900/60 border border-slate-800 rounded-2xl">
          No tienes proyectos activos aún. Crea tu primer proyecto para agrupar tareas.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {projects.map((p) => (
            <div
              key={p.id}
              className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between shadow-sm"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-slate-800 text-cyan-300 border border-cyan-500/30 uppercase font-semibold">
                    {p.category}
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-400">{p.priority}</span>
                </div>

                <h3 className="text-base font-bold text-white mb-1">{p.name}</h3>
                {p.description && (
                  <p className="text-xs text-slate-400 line-clamp-2 mb-4">{p.description}</p>
                )}
              </div>

              <div className="space-y-3 pt-3 border-t border-slate-800/60 mt-3">
                {/* Progress bar */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Progreso</span>
                    <span className="font-semibold text-cyan-400">{p.progress_percentage || 0}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 to-indigo-600 transition-all duration-500"
                      style={{ width: `${p.progress_percentage || 0}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span className="flex items-center gap-1 font-mono">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>
                      {p.completed_tasks || 0} / {p.total_tasks || 0} tareas
                    </span>
                  </span>

                  {p.target_date && (
                    <span className="flex items-center gap-1 font-mono text-indigo-300">
                      <Target className="w-3.5 h-3.5" />
                      <span>{p.target_date}</span>
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Nuevo Proyecto */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Crear Nuevo Proyecto</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateProject} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-300 mb-1">Nombre del Proyecto *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ej. Tesis de Grado en IA"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Descripción y Objetivos</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Alcance del proyecto..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Categoría</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  >
                    <option value="académico">Académico</option>
                    <option value="profesional">Profesional</option>
                    <option value="personal">Personal</option>
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-slate-300 mb-1">Prioridad</label>
                  <select
                    value={priority}
                    onChange={(e: any) => setPriority(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  >
                    <option value="P1">P1 - Crítico</option>
                    <option value="P2">P2 - Alto</option>
                    <option value="P3">P3 - Normal</option>
                    <option value="P4">P4 - Bajo</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Fecha Objetivo</label>
                <input
                  type="date"
                  value={targetDate}
                  onChange={(e) => setTargetDate(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                />
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
                  Crear Proyecto
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
