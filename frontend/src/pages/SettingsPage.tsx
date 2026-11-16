import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Download,
  Smartphone,
  Laptop,
  Apple,
  Globe,
  Bot,
  LogOut,
  CheckCircle2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const SettingsPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isInstalled, setIsInstalled] = useState<boolean>(false);

  useEffect(() => {
    // Escuchar evento de instalación PWA
    const handleBeforeInstall = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);

    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      alert('Para instalar NEXUS: Abre las opciones de tu navegador y selecciona "Instalar aplicación" o "Añadir a la pantalla de inicio".');
      return;
    }
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setIsInstalled(true);
    }
    setDeferredPrompt(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <SettingsIcon className="w-6 h-6 text-slate-400" />
          <span>Configuración & Instalación</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Perfil personal, instalación multiplataforma (PWA) y estado del sistema.
        </p>
      </div>

      {/* PWA Installation Section */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono font-bold uppercase tracking-wider">
              Acceso Directo Multiplataforma
            </span>
            <h2 className="text-lg font-bold text-white">Instalar NEXUS en tu Dispositivo</h2>
            <p className="text-xs text-slate-300 max-w-xl">
              Instala NEXUS como aplicación independiente en Windows, Android o iPhone. Podrás abrirlo directamente desde su icono sin abrir navegadores ni terminales.
            </p>
          </div>

          <button
            onClick={handleInstallClick}
            disabled={isInstalled}
            className={`inline-flex items-center gap-2 px-5 py-3 rounded-xl font-medium text-xs shadow-lg transition-all self-start sm:self-auto ${
              isInstalled
                ? 'bg-slate-800 text-emerald-400 border border-emerald-500/30 cursor-default'
                : 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-cyan-500/20 hover:opacity-95 active:scale-95'
            }`}
          >
            {isInstalled ? (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>NEXUS Instalado</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Instalar Aplicación</span>
              </>
            )}
          </button>
        </div>

        {/* Guides for Windows, Android, iOS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-3 border-t border-slate-800/80">
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
            <div className="flex items-center gap-2 text-white font-semibold text-xs">
              <Laptop className="w-4 h-4 text-cyan-400" />
              <span>Windows (PC)</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              En Chrome o Edge, haz clic en el icono de instalación en la barra de direcciones o presiona el botón "Instalar Aplicación". Se creará un acceso directo en tu escritorio.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
            <div className="flex items-center gap-2 text-white font-semibold text-xs">
              <Smartphone className="w-4 h-4 text-emerald-400" />
              <span>Android</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              En Chrome para Android, pulsa el menú de 3 puntos (⋮) y selecciona <strong>"Instalar aplicación"</strong> o "Añadir a la pantalla de inicio".
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
            <div className="flex items-center gap-2 text-white font-semibold text-xs">
              <Apple className="w-4 h-4 text-slate-200" />
              <span>iPhone (iOS)</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              En Safari, toca el botón de <strong>Compartir</strong> (cuadrado con flecha hacia arriba) y selecciona <strong>"Añadir a pantalla de inicio"</strong>.
            </p>
          </div>
        </div>
      </div>

      {/* Profile & Account Details */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl space-y-4">
        <h2 className="text-base font-bold text-white">Perfil y Cuenta</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-slate-500 block mb-1">Nombre Completo</span>
            <span className="font-semibold text-slate-200">{user?.full_name}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-slate-500 block mb-1">Correo Electrónico</span>
            <span className="font-semibold text-slate-200 font-mono">{user?.email}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-slate-500 block mb-1 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-cyan-400" />
              <span>Zona Horaria</span>
            </span>
            <span className="font-semibold text-cyan-300 font-mono">{user?.timezone || 'America/Bogota'}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-slate-500 block mb-1 flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5 text-indigo-400" />
              <span>Motor de Inteligencia Artificial</span>
            </span>
            <span className="font-semibold text-indigo-300 font-mono">Google Gemini + Tool Execution</span>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 flex justify-between items-center">
          <span className="text-xs text-slate-500">Versión 2.0.0 (Full-Stack PWA)</span>
          <button
            onClick={logout}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 hover:bg-rose-500/20 text-xs font-semibold transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </div>
    </div>
  );
};
