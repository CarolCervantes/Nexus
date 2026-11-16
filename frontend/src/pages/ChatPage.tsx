import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Bot,
  User,
  Plus,
  MessageSquare,
  Sparkles,
  Wrench,
  Clock
} from 'lucide-react';
import { apiService } from '../services/api';
import type { Conversation, Message } from '../types';
import { VoiceButton } from '../components/voice/VoiceButton';

export const ChatPage: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvId, setCurrentConvId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchConversations = async () => {
    try {
      const list = await apiService.chat.getConversations();
      setConversations(list);
      if (list.length > 0 && !currentConvId) {
        setCurrentConvId(list[0].id);
      }
    } catch (err) {
      console.error('Error al cargar conversaciones:', err);
    }
  };

  const fetchMessages = async (convId: number) => {
    try {
      const data = await apiService.chat.getConversation(convId);
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Error al cargar mensajes:', err);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (currentConvId) {
      fetchMessages(currentConvId);
    }
  }, [currentConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleCreateNewConv = async () => {
    try {
      const newConv = await apiService.chat.createConversation('Nueva conversación');
      setConversations([newConv, ...conversations]);
      setCurrentConvId(newConv.id);
      setMessages([]);
    } catch (err) {
      console.error('Error al crear conversación:', err);
    }
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const msg = inputMessage.trim();
    if (!msg || loading) return;

    // Optimistic user message
    const tempUserMsg: Message = {
      id: Date.now(),
      conversation_id: currentConvId || 0,
      sender: 'user',
      content: msg,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setInputMessage('');
    setLoading(true);

    try {
      const assistantMsg = await apiService.chat.sendMessage(msg, currentConvId || undefined);
      setMessages((prev) => [...prev, assistantMsg]);
      // Si era una conversación recién creada, refrescar lista
      fetchConversations();
    } catch (err) {
      console.error('Error al enviar mensaje:', err);
    } finally {
      setLoading(false);
    }
  };

  const lastAssistantMsg = [...messages].reverse().find((m) => m.sender === 'assistant')?.content;

  return (
    <div className="h-[calc(100vh-5.5rem)] md:h-[calc(100vh-3rem)] flex gap-4 max-w-6xl mx-auto">
      {/* Conversations Drawer (Desktop) */}
      <div className="hidden lg:flex flex-col w-72 bg-slate-900/60 border border-slate-800 rounded-2xl p-3 backdrop-blur-xl shrink-0">
        <button
          onClick={handleCreateNewConv}
          className="flex items-center justify-center gap-2 w-full py-2.5 px-3 mb-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-semibold hover:bg-cyan-500/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Nueva Conversación</span>
        </button>

        <div className="flex-1 overflow-y-auto space-y-1 pr-1">
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => setCurrentConvId(c.id)}
              className={`w-full text-left p-2.5 rounded-xl text-xs transition-all ${
                c.id === currentConvId
                  ? 'bg-slate-800 text-white font-medium border border-slate-700/80 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <MessageSquare className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                <span className="truncate font-medium">{c.title}</span>
              </div>
              {c.last_message && (
                <p className="text-[10px] text-slate-500 truncate pl-5.5">{c.last_message}</p>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-xl shadow-xl">
        {/* Chat Header */}
        <div className="p-3.5 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-md shadow-cyan-500/20">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold text-white tracking-wide">NEXUS AI</h2>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              </div>
              <p className="text-[10px] text-slate-400 font-mono">Conectado a persistencia y herramientas</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <VoiceButton
              onTranscript={(text) => {
                setInputMessage(text);
              }}
              lastAssistantResponse={lastAssistantMsg}
            />
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-6 text-slate-400 max-w-md mx-auto">
              <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-4">
                <Sparkles className="w-7 h-7 text-cyan-400" />
              </div>
              <h3 className="text-base font-bold text-white mb-2">¿Cómo te ayudo hoy?</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-6">
                Puedes pedirme que organice tu día, cree una tarea con fecha límite, registre un proyecto, guarde una idea o anote un gasto.
              </p>
              <div className="grid grid-cols-1 gap-2 w-full text-xs">
                <button
                  onClick={() => setInputMessage('¿Qué tengo pendiente hoy?')}
                  className="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-800 text-left text-slate-300 transition-colors"
                >
                  📋 "¿Qué tengo pendiente hoy?"
                </button>
                <button
                  onClick={() => setInputMessage('Añade una tarea urgente para entregar informe')}
                  className="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-800 text-left text-slate-300 transition-colors"
                >
                  ⚡ "Añade una tarea urgente para entregar informe"
                </button>
                <button
                  onClick={() => setInputMessage('Guarda esta idea: sistema de búsqueda semántica')}
                  className="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-800 text-left text-slate-300 transition-colors"
                >
                  💡 "Guarda esta idea: sistema de búsqueda semántica"
                </button>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'assistant' && (
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-sm">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-gradient-to-r from-indigo-600 to-cyan-600 text-white rounded-br-none shadow-md shadow-indigo-600/10'
                      : 'bg-slate-800/80 border border-slate-700/60 text-slate-100 rounded-bl-none shadow-sm'
                  }`}
                >
                  {/* Tool execution indicator badge */}
                  {msg.tool_calls && (
                    <div className="mb-2 inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 text-[10px] font-mono">
                      <Wrench className="w-3 h-3" />
                      <span>Acción en BD: {msg.tool_calls}</span>
                    </div>
                  )}

                  <div className="whitespace-pre-wrap">{msg.content}</div>

                  <div className="mt-1 text-[10px] text-slate-400 text-right opacity-70 flex items-center justify-end gap-1">
                    <Clock className="w-2.5 h-2.5" />
                    <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>

                {msg.sender === 'user' && (
                  <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {loading && (
            <div className="flex gap-3 items-center text-xs text-cyan-400">
              <div className="w-7 h-7 rounded-lg bg-cyan-500/20 flex items-center justify-center text-cyan-400">
                <Bot className="w-4 h-4 animate-spin" />
              </div>
              <div className="flex gap-1 items-center bg-slate-800/80 px-3 py-2 rounded-xl border border-slate-700">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" />
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.2s]" />
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.4s]" />
                <span className="ml-1 text-[11px] text-slate-400 font-mono">NEXUS procesando...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input Box */}
        <form onSubmit={handleSendMessage} className="p-3 bg-slate-900/90 border-t border-slate-800 flex items-center gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Escribe a NEXUS (ej. 'Añade una tarea para mañana...')"
            className="flex-1 bg-slate-950/70 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 transition-colors"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || loading}
            className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-500/20 hover:opacity-90 active:scale-95 transition-all disabled:opacity-40"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
