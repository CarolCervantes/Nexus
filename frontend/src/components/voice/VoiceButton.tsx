import React, { useState } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  lastAssistantResponse?: string;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({ onTranscript, lastAssistantResponse }) => {
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);

  const toggleListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Tu navegador no soporta reconocimiento de voz nativo (Web Speech API). Prueba con Chrome, Edge o Safari.');
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'es-CO';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const text = event.results[0][0].transcript;
        if (text) {
          onTranscript(text);
        }
      };

      recognition.onerror = () => {
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch {
      setIsListening(false);
    }
  };

  const speakLastResponse = () => {
    if (!('speechSynthesis' in window) || !lastAssistantResponse) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    // Limpiar markdown antes de leer
    const cleanText = lastAssistantResponse
      .replace(/[#*`_~]/g, '')
      .replace(/\[(.*?)\]\(.*?\)/g, '$1');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'es-ES';
    utterance.rate = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="flex items-center gap-1.5">
      {/* Mic Button */}
      <button
        type="button"
        onClick={toggleListening}
        title={isListening ? 'Escuchando... (clic para parar)' : 'Hablar con NEXUS'}
        className={`p-2.5 rounded-xl transition-all duration-200 ${
          isListening
            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse'
            : 'text-slate-400 hover:text-cyan-400 hover:bg-slate-800/80 border border-transparent'
        }`}
      >
        {isListening ? <Mic className="w-5 h-5 text-rose-400" /> : <MicOff className="w-5 h-5" />}
      </button>

      {/* TTS Read Aloud Button */}
      {lastAssistantResponse && (
        <button
          type="button"
          onClick={speakLastResponse}
          title={isSpeaking ? 'Detener lectura' : 'Escuchar respuesta de NEXUS'}
          className={`p-2 rounded-lg transition-colors ${
            isSpeaking ? 'text-cyan-400 bg-cyan-500/10' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Volume2 className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
