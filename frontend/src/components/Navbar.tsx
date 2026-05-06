<<<<<<< HEAD
import { NavLink, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, ShieldCheck } from 'lucide-react';
=======
import React from 'react';
import { NavLink, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, ShieldCheck, RefreshCw } from 'lucide-react';
import { API_BASE_URL } from '../config';
>>>>>>> development

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
<<<<<<< HEAD
=======
  const [isUpdating, setIsUpdating] = React.useState(false);

  const handleResetAndScrape = async () => {
    if (!window.confirm('¿Estás seguro de que deseas limpiar la base de datos e iniciar los scrapers? Esta acción borrará todos los coches actuales y tardará entre 30 y 60 minutos en completarse.')) {
      return;
    }

    setIsUpdating(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/reset-and-scrape`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
      });

      const data = await response.json();
      if (response.ok) {
        alert(data.message);
      } else {
        alert(`Error: ${data.detail}`);
      }
    } catch (err) {
      console.error('Failed to reset and scrape', err);
      alert('Error al conectar con el servidor.');
    } finally {
      setIsUpdating(false);
    }
  };
>>>>>>> development

  return (
    <nav className="sticky top-0 z-[1000] px-10 py-6 flex justify-between items-center bg-white/80 backdrop-blur-3xl border-b border-slate-100 shadow-sm transition-all duration-500">
      <Link to="/" className="flex items-center gap-5 group cursor-pointer">
        <div className="relative">
          <div className="bg-slate-900 p-3.5 rounded-[1.25rem] transition-all duration-700 group-hover:rotate-[360deg] shadow-xl group-hover:shadow-accent-500/30">
            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-accent-600 rounded-full border-[4px] border-white shadow-md" />
        </div>
        <div className="flex flex-col -space-y-1.5">
          <h1 className="text-2xl font-black tracking-tighter uppercase font-display leading-none">
            <span className="text-slate-900">Coche</span>
            <span className="text-accent-600">Export</span>
          </h1>
          <span className="text-xs font-bold text-slate-400 tracking-[0.4em] uppercase">Intelligence</span>
        </div>
      </Link>
      
<<<<<<< HEAD
      <div className="absolute left-1/2 -translate-x-1/2 hidden lg:flex items-center gap-14">
        {[
          { label: 'Explorar', path: '/marketplace' },
          { label: 'Favoritos', path: '/favorites' },
        ].map((link) => {
          const isActive = location.pathname.startsWith(link.path);

          return (
            <Link 
              key={link.path}
              to={link.path}
              className={`text-sm font-bold transition-all relative group uppercase tracking-[0.2em] py-2 ${
                isActive ? 'text-slate-900' : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              {link.label}
              <span className={`absolute -bottom-1 left-0 h-1 bg-accent-600 transition-all duration-500 rounded-full ${
                isActive ? 'w-full' : 'w-0 group-hover:w-full'
              }`} />
            </Link>
          );
        })}
      </div>
      
      <div className="flex items-center gap-8">
        {user?.is_admin && (
           <div className="hidden md:flex items-center gap-2.5 px-4 py-2 bg-accent-50 text-accent-700 rounded-2xl border border-accent-100 animate-reveal">
             <ShieldCheck className="w-5 h-5" />
             <span className="text-xs font-black uppercase tracking-widest">Master Admin</span>
=======
      {user && (
        <div className="absolute left-1/2 -translate-x-1/2 hidden lg:flex items-center gap-14">
          {[
            { label: 'Explorar', path: '/marketplace' },
            { label: 'Favoritos', path: '/favorites' },
          ].map((link) => {
            const isActive = location.pathname.startsWith(link.path);

            return (
              <Link 
                key={link.path}
                to={link.path}
                className={`text-sm font-bold transition-all relative group uppercase tracking-[0.2em] py-2 ${
                  isActive ? 'text-slate-900' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                {link.label}
                <span className={`absolute -bottom-1 left-0 h-1 bg-accent-600 transition-all duration-500 rounded-full ${
                  isActive ? 'w-full' : 'w-0 group-hover:w-full'
                }`} />
              </Link>
            );
          })}
        </div>
      )}
      
      <div className="flex items-center gap-8">
        {user?.is_admin && (
           <div className="hidden md:flex items-center gap-4">
             <button
               onClick={handleResetAndScrape}
               disabled={isUpdating}
               className={`flex items-center gap-2.5 px-5 py-2.5 rounded-2xl border transition-all duration-300 font-bold uppercase tracking-widest text-[10px] ${
                 isUpdating 
                 ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed' 
                 : 'bg-red-50 border-red-100 text-red-600 hover:bg-red-600 hover:text-white hover:border-red-600 hover:shadow-lg hover:shadow-red-500/20'
               }`}
             >
               <RefreshCw className={`w-4 h-4 ${isUpdating ? 'animate-spin' : ''}`} />
               {isUpdating ? 'Procesando...' : 'Actualizar Coches'}
             </button>

             <div className="flex items-center gap-2.5 px-4 py-2 bg-accent-50 text-accent-700 rounded-2xl border border-accent-100 animate-reveal">
               <ShieldCheck className="w-5 h-5" />
               <span className="text-xs font-black uppercase tracking-widest">Master Admin</span>
             </div>
>>>>>>> development
           </div>
        )}

        {user ? (
          <div className="flex items-center gap-5 pl-8 border-l-2 border-slate-50">
            <Link 
              to="/profile"
              className="flex items-center gap-4 group"
            >
              <div className="w-12 h-12 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center text-2xl transition-all duration-500 group-hover:bg-white group-hover:border-accent-200 group-hover:shadow-premium group-hover:scale-105 select-none">
                {user.avatar || '😀'}
              </div>
              <div className="hidden md:flex flex-col items-start -space-y-1.5">
                <span className="text-sm font-bold text-slate-900 uppercase tracking-tight truncate max-w-[140px]">{user.full_name || user.username}</span>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{user.is_admin ? 'Intelligence Admin' : 'Socio VIP'}</span>
              </div>
            </Link>
            <button 
              onClick={logout}
              className="w-11 h-11 flex items-center justify-center rounded-2xl text-slate-300 hover:text-accent-600 hover:bg-accent-50 transition-all duration-300 hover:rotate-12"
              title="Finalizar Sesión"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        ) : (
          <button 
            onClick={() => navigate('/login')}
            className="btn btn-primary text-xs uppercase tracking-[0.2em] py-4 px-12 shadow-2xl hover:scale-105 transition-transform"
          >
            Acceso Socios
          </button>
        )}
      </div>
    </nav>
  );
};
