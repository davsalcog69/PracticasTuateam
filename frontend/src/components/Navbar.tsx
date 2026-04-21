import { NavLink, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, ShieldCheck } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

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
