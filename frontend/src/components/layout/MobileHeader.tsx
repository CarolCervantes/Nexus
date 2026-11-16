import React from 'react';
import { Zap } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const MobileHeader: React.FC = () => {
  const { user } = useAuth();

  return (
    <header className="md:hidden flex items-center justify-between px-4 py-3 bg-slate-900/90 border-b border-slate-800 backdrop-blur-xl sticky top-0 z-40">
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-md shadow-cyan-500/20">
          <Zap className="w-4 h-4 text-white" />
        </div>
        <div>
          <span className="font-bold text-sm text-white tracking-wider">NEXUS</span>
          <span className="text-[10px] text-cyan-400 block font-mono">Life Agent</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-indigo-600/30 border border-indigo-400/30 flex items-center justify-center font-bold text-xs text-indigo-300">
          {user?.full_name?.charAt(0) || 'U'}
        </div>
      </div>
    </header>
  );
};
