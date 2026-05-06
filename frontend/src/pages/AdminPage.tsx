import React, { useState, useEffect, useRef } from 'react';
import { RefreshCw, Terminal as TerminalIcon, ShieldCheck, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config';

export const AdminPage: React.FC = () => {
    const { token } = useAuth();
    const [logs, setLogs] = useState<string>('');
    const [logBaseline, setLogBaseline] = useState(0);
    const [isUpdating, setIsUpdating] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const terminalRef = useRef<HTMLDivElement>(null);

    const fetchLogs = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/scraper-logs`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();
            if (response.ok) {
                const newLogs = data.logs;
                const allLines = newLogs.split('\n').filter((l: string) => l.trim());
                
                setLogs(newLogs);
                // If logs were reset on the server, reset the local baseline
                if (allLines.length < logBaseline) {
                    setLogBaseline(0);
                }
            }
        } catch (err) {
            console.error('Failed to fetch logs', err);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 1500);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (terminalRef.current) {
            terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }
    }, [logs, logBaseline]);

    const handleUpdate = async () => {
        setShowConfirm(false);
        setIsUpdating(true);
        setLogBaseline(0);
        try {
            const response = await fetch(`${API_BASE_URL}/admin/reset-and-scrape`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (!response.ok) throw new Error('Failed to start update');
        } catch (err) {
            console.error(err);
            setIsUpdating(false);
        }
    };

    const currentLines = logs.split('\n').filter(l => l.trim()).slice(logBaseline);

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col font-outfit">
            <div className="flex-1 p-8 md:p-12 overflow-y-auto">
                <div className="max-w-6xl mx-auto space-y-12">
                    {/* Header Section */}
                    <header className="flex flex-col md:flex-row md:items-center justify-between gap-8">
                        <div className="space-y-2">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-red-100 text-red-600 rounded-xl">
                                    <ShieldCheck className="w-6 h-6" />
                                </div>
                                <h1 className="text-4xl font-black text-slate-900 tracking-tight">Panel de Control</h1>
                            </div>
                            <p className="text-slate-500 font-medium text-lg">
                                Gestiona la base de datos y monitoriza las tareas de scraping en tiempo real.
                            </p>
                        </div>

                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setShowConfirm(true)}
                                disabled={isUpdating}
                                className={`flex items-center gap-3 px-10 py-5 rounded-[2rem] font-bold uppercase tracking-widest text-sm transition-all duration-300 shadow-xl ${
                                    isUpdating 
                                    ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none' 
                                    : 'bg-red-600 text-white hover:bg-red-700 shadow-red-500/20 active:scale-95'
                                }`}
                            >
                                <RefreshCw className={`w-5 h-5 ${isUpdating ? 'animate-spin' : ''}`} />
                                {isUpdating ? 'Actualizando...' : 'Actualizar Ahora'}
                            </button>
                            
                            <button
                                onClick={() => setLogBaseline(logs.split('\n').filter(l => l.trim()).length)}
                                className="p-5 bg-white text-slate-400 hover:text-slate-600 rounded-[2rem] border border-slate-100 shadow-sm transition-all hover:shadow-md active:scale-95"
                                title="Limpiar Vista"
                            >
                                <TerminalIcon className="w-5 h-5" />
                            </button>
                        </div>
                    </header>

                    {/* Terminal Section */}
                    <section className="bg-slate-950 rounded-[3rem] border border-slate-800 shadow-2xl overflow-hidden flex flex-col h-[650px] animate-in fade-in slide-in-from-bottom-6 duration-1000">
                        {/* Terminal Bar */}
                        <div className="bg-slate-900/80 px-8 py-5 border-b border-slate-800 flex items-center justify-between">
                            <div className="flex gap-2.5">
                                <div className="w-3.5 h-3.5 rounded-full bg-red-500/20 border border-red-500/40" />
                                <div className="w-3.5 h-3.5 rounded-full bg-amber-500/20 border border-amber-500/40" />
                                <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 border border-emerald-500/40" />
                            </div>
                            <span className="text-slate-500 text-[11px] font-bold uppercase tracking-[0.3em] flex items-center gap-3">
                                <span className={`w-2 h-2 rounded-full ${isUpdating ? 'bg-emerald-500 animate-pulse' : 'bg-slate-700'}`} />
                                {isUpdating ? 'System Active' : 'System Standby'}
                            </span>
                        </div>

                        {/* Terminal Log Area */}
                        <div 
                            ref={terminalRef}
                            className="flex-1 p-10 overflow-y-auto font-mono text-[14px] leading-relaxed scrollbar-thin scrollbar-thumb-slate-800 selection:bg-accent-500/30"
                        >
                            {currentLines.length > 0 ? (
                                currentLines.map((line, i) => (
                                    <div key={i} className="mb-2 flex gap-6 group">
                                        <span className="text-slate-700 text-[11px] w-10 text-right select-none pt-1 opacity-50 font-sans">{i + 1}</span>
                                        <span className={`whitespace-pre-wrap ${
                                            line.includes('ERROR') || line.includes('[CRITICAL]') ? 'text-red-400' : 
                                            line.includes('OK') || line.includes('completada') ? 'text-emerald-400' : 
                                            line.includes('[INFO]') ? 'text-sky-400' : 
                                            line.includes('[ADMIN]') ? 'text-purple-400' :
                                            'text-slate-300'
                                        }`}>
                                            {line}
                                        </span>
                                    </div>
                                ))
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-slate-700 space-y-6 opacity-40">
                                    <div className="p-6 bg-slate-900 rounded-full border border-slate-800">
                                        <TerminalIcon className="w-12 h-12" />
                                    </div>
                                    <p className="text-lg italic font-medium tracking-wide">Esperando señales del sistema...</p>
                                </div>
                            )}
                        </div>
                    </section>

                    {/* Stats Footer */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-12">
                        {[
                            { label: 'Estado del Motor', value: isUpdating ? 'Ejecutando' : 'Inactivo', color: isUpdating ? 'text-emerald-600' : 'text-slate-400' },
                            { label: 'Líneas Procesadas', value: currentLines.length, color: 'text-slate-900' },
                            { label: 'Nivel de Seguridad', value: 'Máximo (SSL)', color: 'text-red-600' }
                        ].map((stat, i) => (
                            <div key={i} className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm flex flex-col gap-2">
                                <span className="text-[11px] font-black uppercase tracking-widest text-slate-400">{stat.label}</span>
                                <span className={`text-2xl font-black tracking-tight ${stat.color}`}>{stat.value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Premium Confirmation Modal Overlay */}
            {showConfirm && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 md:p-12">
                    <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-xl animate-in fade-in duration-500" onClick={() => setShowConfirm(false)} />
                    
                    <div className="relative bg-white rounded-[3rem] shadow-[0_32px_64px_-16px_rgba(0,0,0,0.3)] max-w-lg w-full p-12 border border-white/20 animate-in zoom-in-95 slide-in-from-bottom-12 duration-500">
                        <button 
                            onClick={() => setShowConfirm(false)}
                            className="absolute top-8 right-8 p-3 text-slate-300 hover:text-slate-900 transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>

                        <div className="w-24 h-24 bg-red-50 rounded-[2.5rem] flex items-center justify-center mb-10 shadow-inner">
                            <RefreshCw className="w-12 h-12 text-red-600" />
                        </div>
                        
                        <h2 className="text-3xl font-black text-slate-900 mb-6 tracking-tight leading-tight">
                            ¿Confirmar actualización completa?
                        </h2>
                        
                        <p className="text-slate-500 font-medium text-lg mb-12 leading-relaxed">
                            Esta acción <span className="text-red-600 font-bold">borrará todos los datos actuales</span> de vehículos e iniciará un nuevo ciclo de scraping. El proceso no se puede deshacer una vez iniciado.
                        </p>
                        
                        <div className="flex flex-col sm:flex-row gap-5">
                            <button
                                onClick={() => setShowConfirm(false)}
                                className="flex-1 px-10 py-5 rounded-[1.5rem] font-bold text-slate-400 hover:text-slate-900 hover:bg-slate-50 transition-all duration-300"
                            >
                                Descartar
                            </button>
                            <button
                                onClick={handleUpdate}
                                className="flex-1 px-10 py-5 rounded-[1.5rem] bg-slate-900 text-white font-bold shadow-2xl shadow-slate-900/20 hover:bg-black active:scale-95 transition-all duration-300"
                            >
                                Iniciar Proceso
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
