import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, UserPlus, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (user) {
      navigate('/marketplace');
    }
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        login(data.access_token);
        navigate('/marketplace');
      } else {
        setError(data.detail || 'Fallo al iniciar sesión. Compruebe sus credenciales.');
      }
    } catch (err) {
      setError('Error de conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-100px)] flex items-center justify-center p-8 animate-reveal">
      <div className="w-full max-w-md bg-white rounded-[3rem] border border-slate-100/50 shadow-premium p-12 relative overflow-hidden">
        {/* Decorative Element */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-accent-50 rounded-full blur-3xl opacity-50" />
        
        <div className="text-center mb-12 relative z-10">
          <div className="bg-slate-900 w-20 h-20 rounded-[2rem] flex items-center justify-center mx-auto mb-8 shadow-xl shadow-slate-200">
            <LogIn className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold tracking-tighter text-slate-900 leading-none">Intelligence</h1>
          <p className="text-slate-400 mt-3 text-xs font-bold uppercase tracking-widest">Portal de Acceso Exclusivo</p>
        </div>

        {error && (
          <div className="bg-accent-50 border border-accent-100 p-5 rounded-2xl flex items-center gap-4 text-accent-700 text-[10px] font-bold uppercase tracking-wider mb-8 animate-reveal">
            <AlertCircle className="w-5 h-5 shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8 relative z-10">
          <div className="space-y-3">
            <label className="text-[9px] font-bold text-slate-400 uppercase tracking-[0.2em] ml-2">Identificador de Usuario</label>
            <input 
              type="text" 
              required
              className="input-premium"
              placeholder="Ej: master_inversor"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div className="space-y-3">
            <label className="text-[9px] font-bold text-slate-400 uppercase tracking-[0.2em] ml-2">Clave de Seguridad</label>
            <input 
              type="password" 
              required
              className="input-premium"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="btn btn-primary w-full py-5 text-[11px] uppercase tracking-[0.3em] shadow-xl disabled:opacity-50 mt-4"
          >
            {loading ? 'Validando Credenciales...' : 'Desbloquear Acceso'}
          </button>
        </form>

        <div className="mt-12 pt-10 border-t border-slate-50 text-center relative z-10">
          <p className="text-[10px] text-slate-400 font-medium italic">
            Consulte con su administrador de flota para obtener credenciales de acceso nivel VIP.
          </p>
        </div>
      </div>
    </div>
  );
};
