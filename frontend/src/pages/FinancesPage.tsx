import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  Plus,
  TrendingUp,
  TrendingDown,
  PieChart,
  Trash2,
  X
} from 'lucide-react';
import { apiService } from '../services/api';
import type { FinanceRecord, FinanceSummary } from '../types';

export const FinancesPage: React.FC = () => {
  const [records, setRecords] = useState<FinanceRecord[]>([]);
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);

  // Form state
  const [type, setType] = useState<'gasto' | 'ingreso'>('gasto');
  const [category, setCategory] = useState('alimentacion');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [recList, sumData] = await Promise.all([
        apiService.finances.list(),
        apiService.finances.getSummary()
      ]);
      setRecords(recList);
      setSummary(sumData);
    } catch (err) {
      console.error('Error al cargar finanzas:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!amount || Number(amount) <= 0) return;

    try {
      await apiService.finances.create({
        type,
        category,
        amount: Number(amount),
        description,
        date
      });
      setShowModal(false);
      setAmount('');
      setDescription('');
      fetchData();
    } catch (err) {
      console.error('Error al crear registro financiero:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Eliminar este movimiento?')) return;
    try {
      await apiService.finances.delete(id);
      fetchData();
    } catch (err) {
      console.error('Error al eliminar registro:', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <DollarSign className="w-6 h-6 text-emerald-400" />
            <span>Finanzas Personales</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Registro manual, control de presupuestos y resumen de gastos del mes.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-600 text-white font-medium text-xs shadow-md shadow-emerald-500/20 hover:opacity-95 active:scale-95 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Registrar Movimiento</span>
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Ingresos del Mes</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400">
            ${summary?.total_income.toLocaleString()} COP
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Gastos del Mes</span>
            <TrendingDown className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-rose-400">
            ${summary?.total_expense.toLocaleString()} COP
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Balance Neto</span>
            <PieChart className="w-4 h-4 text-cyan-400" />
          </div>
          <p
            className={`text-2xl font-bold ${
              (summary?.net_balance || 0) >= 0 ? 'text-white' : 'text-rose-400'
            }`}
          >
            ${summary?.net_balance.toLocaleString()} COP
          </p>
        </div>
      </div>

      {/* Movements Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden divide-y divide-slate-800/80 backdrop-blur-xl">
        <div className="p-4 bg-slate-900/90 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">Historial de Movimientos</h2>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Cargando movimientos...</div>
        ) : records.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            Sin movimientos registrados este mes. Haz clic en "Registrar Movimiento" para añadir uno.
          </div>
        ) : (
          records.map((rec) => (
            <div
              key={rec.id}
              className="p-4 flex items-center justify-between gap-3 hover:bg-slate-800/30 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                    rec.type === 'ingreso' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                  }`}
                >
                  {rec.type === 'ingreso' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                </div>

                <div>
                  <p className="text-sm font-medium text-white">{rec.description || rec.category}</p>
                  <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                    <span className="capitalize">{rec.category}</span>
                    <span>•</span>
                    <span className="font-mono">{rec.date}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span
                  className={`text-sm font-bold font-mono ${
                    rec.type === 'ingreso' ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {rec.type === 'ingreso' ? '+' : '-'}${rec.amount.toLocaleString()}
                </span>
                <button
                  onClick={() => handleDelete(rec.id)}
                  className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
                  title="Eliminar"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal Nuevo Movimiento */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Registrar Movimiento Financiero</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateRecord} className="space-y-4 text-xs">
              <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800">
                <button
                  type="button"
                  onClick={() => setType('gasto')}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    type === 'gasto' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'text-slate-400'
                  }`}
                >
                  Gasto
                </button>
                <button
                  type="button"
                  onClick={() => setType('ingreso')}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    type === 'ingreso' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400'
                  }`}
                >
                  Ingreso
                </button>
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Monto ($ COP) *</label>
                <input
                  type="number"
                  required
                  min={1}
                  step={100}
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="Ej. 45000"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Categoría</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm"
                >
                  <option value="alimentacion">Alimentación y Supermercado</option>
                  <option value="transporte">Transporte y Movilidad</option>
                  <option value="servicios">Servicios y Suscripciones</option>
                  <option value="educacion">Educación y Cursos</option>
                  <option value="ocio">Ocio y Entretenimiento</option>
                  <option value="salud">Salud y Bienestar</option>
                  <option value="salario">Salario / Honorarios</option>
                  <option value="otro">Otro</option>
                </select>
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Descripción / Concepto</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Ej. Almuerzo con equipo de trabajo"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Fecha</label>
                <input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
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
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-600 text-white font-medium shadow-md shadow-emerald-500/20"
                >
                  Guardar Movimiento
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
