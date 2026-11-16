import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Bot, CheckSquare, Calendar, MoreHorizontal } from 'lucide-react';

export const BottomNav: React.FC = () => {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-slate-900/95 border-t border-slate-800 backdrop-blur-xl flex items-center justify-around px-2 z-50">
      <NavLink
        to="/"
        end
        className={({ isActive }) =>
          `flex flex-col items-center justify-center w-14 py-1 rounded-xl transition-colors ${
            isActive ? 'text-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`
        }
      >
        <LayoutDashboard className="w-5 h-5 mb-0.5" />
        <span className="text-[10px]">Inicio</span>
      </NavLink>

      <NavLink
        to="/tasks"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center w-14 py-1 rounded-xl transition-colors ${
            isActive ? 'text-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`
        }
      >
        <CheckSquare className="w-5 h-5 mb-0.5" />
        <span className="text-[10px]">Tareas</span>
      </NavLink>

      {/* Floating Center Chat Button */}
      <NavLink
        to="/chat"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center -mt-5 w-12 h-12 rounded-full bg-gradient-to-tr from-cyan-500 to-indigo-600 shadow-lg shadow-cyan-500/30 text-white ${
            isActive ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-slate-900' : ''
          }`
        }
      >
        <Bot className="w-6 h-6" />
      </NavLink>

      <NavLink
        to="/calendar"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center w-14 py-1 rounded-xl transition-colors ${
            isActive ? 'text-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`
        }
      >
        <Calendar className="w-5 h-5 mb-0.5" />
        <span className="text-[10px]">Agenda</span>
      </NavLink>

      <NavLink
        to="/settings"
        className={({ isActive }) =>
          `flex flex-col items-center justify-center w-14 py-1 rounded-xl transition-colors ${
            isActive ? 'text-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`
        }
      >
        <MoreHorizontal className="w-5 h-5 mb-0.5" />
        <span className="text-[10px]">Más</span>
      </NavLink>
    </nav>
  );
};
