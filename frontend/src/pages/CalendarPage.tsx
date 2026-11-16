import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Plus, MapPin, Clock, Trash2, X } from 'lucide-react';
import { apiService } from '../services/api';
import type { EventItem } from '../types';

export const CalendarPage: React.FC = () => {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [location, setLocation] = useState('');
  const [isAllDay, setIsAllDay] = useState(false);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const data = await apiService.events.list();
      setEvents(data);
    } catch (err) {
      console.error('Error al cargar eventos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !startTime || !endTime) return;

    try {
      await apiService.events.create({
        title,
        description,
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        location,
        is_all_day: isAllDay
      });
      setShowModal(false);
      setTitle('');
      setDescription('');
      setStartTime('');
      setEndTime('');
      setLocation('');
      fetchEvents();
    } catch (err) {
      console.error('Error al crear evento:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Eliminar este evento de tu agenda?')) return;
    try {
      await apiService.events.delete(id);
      fetchEvents();
    } catch (err) {
      console.error('Error al eliminar evento:', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <CalendarIcon className="w-6 h-6 text-indigo-400" />
            <span>Agenda y Calendario</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Zona horaria activa: <span className="text-cyan-400 font-mono">America/Bogota</span>
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-medium text-xs shadow-md shadow-cyan-500/20 hover:opacity-95 active:scale-95 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Nuevo Evento</span>
        </button>
      </div>

      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl divide-y divide-slate-800/80 overflow-hidden backdrop-blur-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Cargando eventos...</div>
        ) : events.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            No tienes eventos agendados. Haz clic en "Nuevo Evento" para programar una reunión o entrega.
          </div>
        ) : (
          events.map((ev) => (
            <div
              key={ev.id}
              className="p-4 flex items-center justify-between gap-3 hover:bg-slate-800/30 transition-colors"
            >
              <div className="space-y-1">
                <h3 className="text-sm font-semibold text-white">{ev.title}</h3>
                {ev.description && <p className="text-xs text-slate-400">{ev.description}</p>}
                <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1 font-mono text-cyan-400">
                    <Clock className="w-3 h-3" />
                    <span>
                      {new Date(ev.start_time).toLocaleString('es-CO', {
                        dateStyle: 'short',
                        timeStyle: 'short'
                      })}{' '}
                      -{' '}
                      {new Date(ev.end_time).toLocaleTimeString('es-CO', {
                        timeStyle: 'short'
                      })}
                    </span>
                  </span>
                  {ev.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-indigo-400" />
                      <span>{ev.location}</span>
                    </span>
                  )}
                </div>
              </div>

              <button
                onClick={() => handleDelete(ev.id)}
                className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                title="Eliminar evento"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Modal Nuevo Evento */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Agendar Evento</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateEvent} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-300 mb-1">Título del Evento *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ej. Reunión de seguimiento de proyecto"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Inicio *</label>
                  <input
                    type="datetime-local"
                    required
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  />
                </div>

                <div>
                  <label className="block font-medium text-slate-300 mb-1">Fin *</label>
                  <input
                    type="datetime-local"
                    required
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Ubicación o Enlace</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Ej. Google Meet o Sala 402"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Descripción</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Puntos a tratar..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="allDay"
                  checked={isAllDay}
                  onChange={(e) => setIsAllDay(e.target.checked)}
                  className="rounded bg-slate-950 border-slate-800 text-cyan-500"
                />
                <label htmlFor="allDay" className="text-slate-300 cursor-pointer">
                  Evento de todo el día
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
                  Guardar Evento
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
