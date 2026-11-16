import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Search, Tag, Pin, Trash2, X } from 'lucide-react';
import { apiService } from '../services/api';
import type { Note } from '../types';

export const NotesPage: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [search, setSearch] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);

  // Form state
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState<'idea' | 'nota' | 'recurso' | 'referencia'>('nota');
  const [tags, setTags] = useState('');
  const [isPinned, setIsPinned] = useState(false);

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const data = await apiService.notes.list(categoryFilter || undefined, search || undefined);
      setNotes(data);
    } catch (err) {
      console.error('Error al cargar notas:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, [categoryFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchNotes();
  };

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    try {
      await apiService.notes.create({
        title,
        content,
        category,
        tags,
        is_pinned: isPinned
      });
      setShowModal(false);
      setTitle('');
      setContent('');
      setCategory('nota');
      setTags('');
      setIsPinned(false);
      fetchNotes();
    } catch (err) {
      console.error('Error al crear nota:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Deseas eliminar esta nota?')) return;
    try {
      await apiService.notes.delete(id);
      fetchNotes();
    } catch (err) {
      console.error('Error al eliminar nota:', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <BookOpen className="w-6 h-6 text-cyan-400" />
            <span>Notas y Conocimiento</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Almacena ideas, resúmenes, enlaces y referencias de consulta rápida.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-medium text-xs shadow-md shadow-cyan-500/20 hover:opacity-95 active:scale-95 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Nueva Nota</span>
        </button>
      </div>

      {/* Search & Category Filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <form onSubmit={handleSearch} className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar en notas por título, contenido o etiqueta..."
            className="w-full bg-slate-900/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </form>

        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {['', 'idea', 'nota', 'recurso', 'referencia'].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                categoryFilter === cat
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {cat ? cat.charAt(0).toUpperCase() + cat.slice(1) : 'Todas'}
            </button>
          ))}
        </div>
      </div>

      {/* Notes Grid */}
      {loading ? (
        <div className="p-8 text-center text-slate-500 text-sm">Cargando notas...</div>
      ) : notes.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-sm bg-slate-900/60 border border-slate-800 rounded-2xl">
          No hay notas guardadas con estos criterios. Haz clic en "Nueva Nota" para comenzar.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {notes.map((note) => (
            <div
              key={note.id}
              className={`bg-slate-900/70 border rounded-2xl p-4 flex flex-col justify-between shadow-sm transition-all ${
                note.is_pinned ? 'border-cyan-500/40 bg-slate-900/90' : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-cyan-300 border border-slate-700 uppercase font-semibold">
                    {note.category}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {note.is_pinned && <Pin className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400/20" />}
                    <button
                      onClick={() => handleDelete(note.id)}
                      className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                      title="Eliminar"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <h3 className="text-sm font-bold text-white mb-1.5">{note.title}</h3>
                <p className="text-xs text-slate-300 whitespace-pre-wrap leading-relaxed line-clamp-6">
                  {note.content}
                </p>
              </div>

              {note.tags && (
                <div className="pt-3 border-t border-slate-800/60 mt-3 flex flex-wrap gap-1">
                  {note.tags.split(',').map((tag, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 font-mono"
                    >
                      <Tag className="w-2.5 h-2.5 text-indigo-400" />
                      <span>{tag.trim()}</span>
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modal Nueva Nota */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Guardar Nueva Nota / Idea</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateNote} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-300 mb-1">Título *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ej. Arquitectura RAG en SQLite"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Categoría</label>
                  <select
                    value={category}
                    onChange={(e: any) => setCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  >
                    <option value="nota">Nota de clase / resumen</option>
                    <option value="idea">Idea de proyecto</option>
                    <option value="recurso">Recurso / enlace</option>
                    <option value="referencia">Referencia permanente</option>
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-slate-300 mb-1">Etiquetas (separadas por coma)</label>
                  <input
                    type="text"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="ia, tesina, react"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Contenido *</label>
                <textarea
                  rows={5}
                  required
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Escribe el contenido o los puntos clave..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm leading-relaxed"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="pin"
                  checked={isPinned}
                  onChange={(e) => setIsPinned(e.target.checked)}
                  className="rounded bg-slate-950 border-slate-800 text-cyan-500 focus:ring-0"
                />
                <label htmlFor="pin" className="text-slate-300 cursor-pointer">
                  Fijar nota en la parte superior
                </label>
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
                  Guardar Nota
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
