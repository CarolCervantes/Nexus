import React, { useState, useEffect } from 'react';
import { Brain, Plus, Trash2, ShieldCheck, X } from 'lucide-react';
import { apiService } from '../services/api';
import type { Memory } from '../types';

export const MemoriesPage: React.FC = () => {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);

  // Form state
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');
  const [level, setLevel] = useState<'permanent' | 'operational' | 'historical'>('permanent');
  const [category, setCategory] = useState('preferencia');

  const fetchMemories = async () => {
    try {
      setLoading(true);
      const data = await apiService.memories.list(levelFilter || undefined);
      setMemories(data);
    } catch (err) {
      console.error('Error al cargar memorias:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, [levelFilter]);

  const handleCreateMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!key.trim() || !value.trim()) return;

    try {
      await apiService.memories.create({
        key,
        value,
        level,
        category
      });
      setShowModal(false);
      setKey('');
      setValue('');
      fetchMemories();
    } catch (err) {
      console.error('Error al guardar recuerdo:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Seguro que deseas olvidar o eliminar este recuerdo?')) return;
    try {
      await apiService.memories.delete(id);
      fetchMemories();
    } catch (err) {
      console.error('Error al eliminar recuerdo:', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Brain className="w-6 h-6 text-cyan-400" />
            <span>Memoria Persistente de NEXUS</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Transparencia total: consulta, corrige o elimina los recuerdos y preferencias que NEXUS almacena en la nube.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-medium text-xs shadow-md shadow-cyan-500/20 hover:opacity-95 active:scale-95 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Nuevo Recuerdo</span>
        </button>
      </div>

      {/* Info card */}
      <div className="p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 shrink-0 text-cyan-400 mt-0.5" />
        <div className="text-xs leading-relaxed">
          <p className="font-semibold text-white">Privacidad y Control Real</p>
          <p className="text-slate-400 mt-0.5">
            NEXUS nunca almacena contraseñas ni datos bancarios en texto plano. Cada recuerdo listado aquí se inyecta en el contexto de la IA para personalizar tu experiencia en todos tus dispositivos.
          </p>
        </div>
      </div>

      {/* Level Filters */}
      <div className="flex items-center gap-2">
        {[
          { id: '', label: 'Todos los Niveles' },
          { id: 'permanent', label: 'A. Permanente (Preferencias/Hábitos)' },
          { id: 'operational', label: 'B. Operativo (Foco/Proyectos vivos)' },
          { id: 'historical', label: 'C. Histórico (Decisiones pasadas)' }
        ].map((lvl) => (
          <button
            key={lvl.id}
            onClick={() => setLevelFilter(lvl.id)}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              levelFilter === lvl.id
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            {lvl.label}
          </button>
        ))}
      </div>

      {/* Memories List */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden divide-y divide-slate-800/80 backdrop-blur-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Cargando memorias...</div>
        ) : memories.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            No hay recuerdos registrados en este nivel.
          </div>
        ) : (
          memories.map((mem) => (
            <div
              key={mem.id}
              className="p-4 flex items-center justify-between gap-4 hover:bg-slate-800/30 transition-colors"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-cyan-300 font-mono font-bold uppercase">
                    {mem.level}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">[{mem.category}]</span>
                  <h3 className="text-sm font-semibold text-white">{mem.key}</h3>
                </div>
                <p className="text-xs text-slate-300 whitespace-pre-wrap">{mem.value}</p>
              </div>

              <button
                onClick={() => handleDelete(mem.id)}
                className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors shrink-0"
                title="Olvidar / Eliminar"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Modal Nuevo Recuerdo */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Añadir Recuerdo a NEXUS</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateMemory} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Nivel de Memoria</label>
                  <select
                    value={level}
                    onChange={(e: any) => setLevel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  >
                    <option value="permanent">Permanente</option>
                    <option value="operational">Operativa</option>
                    <option value="historical">Histórica</option>
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-slate-300 mb-1">Categoría</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  >
                    <option value="preferencia">Preferencia</option>
                    <option value="objetivo">Objetivo</option>
                    <option value="dato_personal">Dato Personal</option>
                    <option value="decision">Decisión Clave</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Identificador / Clave *</label>
                <input
                  type="text"
                  required
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                  placeholder="Ej. horario_maxima_concentracion"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Contenido / Regla que NEXUS debe recordar *</label>
                <textarea
                  rows={3}
                  required
                  value={value}
                  onChange={(e) => setValue(e.target.value)}
                  placeholder="Ej. Trabajar en bloques de 50 minutos entre las 08:00 y las 12:00..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
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
                  Guardar Recuerdo
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
