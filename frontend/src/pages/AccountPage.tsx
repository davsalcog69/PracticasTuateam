import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  User as UserIcon, 
  Lock, 
  History, 
  ShieldCheck, 
  CheckCircle, 
  AlertCircle, 
  ArrowLeft,
  LogOut,
  UserPlus,
  Smile,
  ShieldAlert
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const AVATARS = ['😀', '😎', '🚗', '🔥', '⭐'];

export const AccountPage: React.FC = () => {
  const { user, token, logout, updateUser } = useAuth();
  
  // Personal Data State
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [selectedAvatar, setSelectedAvatar] = useState(user?.avatar || '😀');
  
  // Password State
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Admin: Create User State
  const [newUsername, setNewUsername] = useState('');
  const [newDisplayName, setNewDisplayName] = useState('');
  const [newPass, setNewPass] = useState('');
  const [isAdminNew, setIsAdminNew] = useState(false);
  
  // UI State
  const [currentSection, setCurrentSection] = useState<'profile' | 'security' | 'activity' | 'admin'>('profile');
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recentVehicles, setRecentVehicles] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setSelectedAvatar(user.avatar || '😀');
    }
  }, [user]);

  useEffect(() => {
    if (currentSection === 'activity' && token) {
      const fetchActivity = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/user/recent-cars`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (response.ok) {
            const data = await response.json();
            setRecentVehicles(data);
          }
        } catch (err) {
          console.error('Failed to fetch activity', err);
        }
      };
      fetchActivity();
    }
  }, [currentSection, token]);

  const handleUpdateAvatar = async (emoji: string) => {
    setSuccess(null);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/user/update`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ avatar: emoji })
      });
      
      if (response.ok) {
        setSelectedAvatar(emoji);
        updateUser({ avatar: emoji });
        setSuccess('Avatar actualizado');
      }
    } catch (err) {
      setError('Error al actualizar avatar');
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(null);
    setError(null);
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/user/update`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ full_name: fullName })
      });
      
      if (response.ok) {
        setSuccess('Perfil actualizado correctamente');
        updateUser({ full_name: fullName });
      } else {
        setError('No se pudo actualizar el perfil');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(null);
    setError(null);
    setLoading(true);

    if (newPassword !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/user/password`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
      });
      
      if (response.ok) {
        setSuccess('Contraseña cambiada correctamente');
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      } else {
        const data = await response.json();
        setError(data.detail || 'Fallo al cambiar la contraseña');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(null);
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/user/admin/create-user`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ 
          username: newUsername, 
          password: newPass, 
          full_name: newDisplayName,
          is_admin: isAdminNew
        })
      });
      
      if (response.ok) {
        setSuccess(`Usuario "${newUsername}" creado con éxito`);
        setNewUsername('');
        setNewPass('');
        setNewDisplayName('');
        setIsAdminNew(false);
      } else {
        const data = await response.json();
        setError(data.detail || 'Fallo al crear usuario');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <div className="flex flex-col md:flex-row gap-10">
        
        {/* Sidebar Nav */}
        <aside className="w-full md:w-72 space-y-2">
          <div className="bg-white rounded-3xl border border-slate-100 shadow-soft p-8 mb-6 transition-colors">
            <div className="flex flex-col items-center text-center">
              <div className="w-24 h-24 rounded-full bg-slate-50 border-4 border-white shadow-md flex items-center justify-center text-5xl mb-4 select-none">
                {user.avatar}
              </div>
              <h3 className="font-bold text-slate-900 uppercase tracking-tight">
                {user.full_name || user.username}
              </h3>
              <div className="flex items-center gap-1.5 mt-2">
                {user.is_admin ? (
                   <span className="flex items-center gap-1 px-2 py-0.5 bg-primary-50 text-primary-600 text-[9px] font-bold uppercase tracking-widest border border-primary-100 rounded-lg">
                     <ShieldCheck className="w-3 h-3" /> Admin
                   </span>
                ) : (
                  <span className="px-2 py-0.5 bg-slate-100 text-slate-500 text-[9px] font-bold uppercase tracking-widest border border-slate-200 rounded-lg">
                    Socio
                  </span>
                )}
              </div>
            </div>
          </div>

          <nav className="space-y-1">
            <button 
              onClick={() => setCurrentSection('profile')}
              className={`w-full flex items-center gap-3 px-6 py-4 rounded-2xl text-xs font-bold transition-all ${
                currentSection === 'profile' ? 'bg-slate-900 text-white shadow-lg' : 'text-slate-500 hover:bg-white hover:text-slate-900 mb-1'
              }`}
            >
              <UserIcon className="w-4 h-4" />
              Datos Personales
            </button>
            <button 
              onClick={() => setCurrentSection('security')}
              className={`w-full flex items-center gap-3 px-6 py-4 rounded-2xl text-xs font-bold transition-all ${
                currentSection === 'security' ? 'bg-slate-900 text-white shadow-lg' : 'text-slate-500 hover:bg-white hover:text-slate-900 mb-1'
              }`}
            >
              <Lock className="w-4 h-4" />
              Seguridad
            </button>
            <button 
              onClick={() => setCurrentSection('activity')}
              className={`w-full flex items-center gap-3 px-6 py-4 rounded-2xl text-xs font-bold transition-all ${
                currentSection === 'activity' ? 'bg-slate-900 text-white shadow-lg' : 'text-slate-500 hover:bg-white hover:text-slate-900 mb-1'
              }`}
            >
              <History className="w-4 h-4" />
              Actividad Reciente
            </button>

            {user.is_admin && (
              <button 
                onClick={() => setCurrentSection('admin')}
                className={`w-full flex items-center gap-3 px-6 py-4 rounded-2xl text-xs font-bold transition-all ${
                  currentSection === 'admin' ? 'bg-primary-600 text-white shadow-lg' : 'text-primary-500 hover:bg-primary-50 mb-1'
                }`}
              >
                <UserPlus className="w-4 h-4" />
                Gestión Usuarios
              </button>
            )}

            <hr className="my-4 border-slate-100" />
            <button 
              onClick={logout}
              className="w-full flex items-center gap-3 px-6 py-4 rounded-2xl text-xs font-bold text-accent-600 hover:bg-accent-50 transition-all"
            >
              <LogOut className="w-4 h-4" />
              Cerrar Sesión
            </button>
          </nav>

          <Link to="/" className="flex items-center gap-2 text-[10px] font-bold text-slate-400 hover:text-slate-600 uppercase tracking-widest px-6 pt-4">
            <ArrowLeft className="w-3 h-3" />
            Volver al Marketplace
          </Link>
        </aside>

        {/* Content Area */}
        <div className="flex-1 space-y-6">
          
          {/* Status Messages */}
          {success && (
            <div className="bg-green-50 border border-green-100 p-4 rounded-2xl flex items-center gap-3 text-green-700 text-xs font-semibold animate-in">
              <CheckCircle className="w-4 h-4" />
              {success}
            </div>
          )}
          {error && (
            <div className="bg-accent-50 border border-accent-100 p-4 rounded-2xl flex items-center gap-3 text-accent-700 text-xs font-semibold animate-in">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          {currentSection === 'profile' && (
            <div className="bg-white rounded-[2rem] border border-slate-100 shadow-soft p-10 animate-in space-y-10 transition-colors">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight text-slate-900 mb-2">Datos Personales</h2>
                <p className="text-sm text-slate-500">Gestione su identidad visual y datos de contacto.</p>
              </div>

              <div className="space-y-6">
                <div className="flex items-center gap-2 mb-4">
                  <Smile className="w-4 h-4 text-slate-400" />
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Seleccionar Avatar</label>
                </div>
                <div className="flex gap-4">
                  {AVATARS.map(emoji => (
                    <button
                      key={emoji}
                      onClick={() => handleUpdateAvatar(emoji)}
                      className={`w-14 h-14 rounded-2xl flex items-center justify-center text-3xl transition-all border-2 ${
                        selectedAvatar === emoji 
                        ? 'border-primary-500 bg-primary-50 scale-110 shadow-md' 
                        : 'border-slate-100 hover:border-slate-300 hover:bg-slate-50 bg-white'
                      }`}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>

              <hr className="border-slate-100" />

              <form onSubmit={handleUpdateProfile} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Nombre Completo</label>
                    <input 
                      type="text" 
                      className="input-field" 
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Nombre de Usuario</label>
                    <input 
                      type="text" 
                      disabled 
                      className="input-field bg-slate-50 text-slate-400 cursor-not-allowed" 
                      value={user.username}
                    />
                  </div>
                </div>

                <button 
                  type="submit" 
                  disabled={loading}
                  className="btn btn-primary px-10 py-4 text-[10px] uppercase tracking-widest shadow-lg disabled:opacity-50"
                >
                  {loading ? 'Guardando...' : 'Guardar Cambios'}
                </button>
              </form>
            </div>
          )}

          {currentSection === 'security' && (
            <div className="bg-white rounded-[2rem] border border-slate-100 shadow-soft p-10 animate-in space-y-10 transition-colors">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight text-slate-900 mb-2">Seguridad</h2>
                <p className="text-sm text-slate-500">Actualice su contraseña para mantener protegidas sus oportunidades.</p>
              </div>

              <form onSubmit={handleChangePassword} className="space-y-8 max-w-lg">
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Contraseña Actual</label>
                  <input 
                    type="password" 
                    className="input-field" 
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Nueva Contraseña</label>
                  <input 
                    type="password" 
                    className="input-field" 
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Confirmar Nueva Contraseña</label>
                  <input 
                    type="password" 
                    className="input-field" 
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>

                <button 
                  type="submit" 
                  disabled={loading}
                  className="btn btn-primary px-10 py-4 text-[10px] uppercase tracking-widest shadow-lg disabled:opacity-50"
                >
                  {loading ? 'Procesando...' : 'Actualizar Contraseña'}
                </button>
              </form>
            </div>
          )}

          {currentSection === 'activity' && (
            <div className="bg-white rounded-[2rem] border border-slate-100 shadow-soft p-10 animate-in space-y-8 transition-colors">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight text-slate-900 mb-2">Historial de Búsquedas</h2>
                <p className="text-sm text-slate-500">Últimos vehículos analizados en el Marketplace.</p>
              </div>

              <div className="space-y-3">
                {recentVehicles.length > 0 ? (
                  recentVehicles.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-6 bg-slate-50 rounded-2xl border border-slate-100 group hover:bg-white hover:shadow-md transition-all">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-white rounded-xl border border-slate-200 flex items-center justify-center text-primary-600 shadow-sm">
                          <History className="w-6 h-6" />
                        </div>
                        <div>
                          <h4 className="font-bold text-slate-900 group-hover:text-primary-600 transition-colors">{item.model_name}</h4>
                          <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Visto el {new Date(item.viewed_at).toLocaleDateString()} a las {new Date(item.viewed_at).toLocaleTimeString()}</p>
                        </div>
                      </div>
                      <Link 
                        to="/" 
                        className="btn btn-secondary py-2 px-4 shadow-sm"
                      >
                        Ver de nuevo
                      </Link>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-20 border-2 border-dashed border-slate-100 rounded-3xl">
                     <History className="w-10 h-10 text-slate-200 mx-auto mb-4" />
                     <p className="text-slate-400 font-medium">No hay actividad reciente.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {currentSection === 'admin' && user.is_admin && (
             <div className="bg-white rounded-[2rem] border border-slate-100 shadow-soft p-10 animate-in space-y-10 transition-colors border-primary-100">
               <div>
                 <div className="flex items-center gap-3 mb-2">
                   <ShieldCheck className="w-6 h-6 text-primary-600" />
                   <h2 className="text-2xl font-semibold tracking-tight text-slate-900">Gestión de Usuarios</h2>
                 </div>
                 <p className="text-sm text-slate-500">Alta de nuevos socios en la red privada de arbitraje.</p>
               </div>

               <div className="bg-primary-50/30 p-8 rounded-[2rem] border border-primary-50">
                 <h3 className="text-[10px] font-bold text-primary-600 uppercase tracking-widest mb-6">Nuevo Usuario</h3>
                 <form onSubmit={handleCreateUser} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Usuario (ID de acceso)</label>
                      <input 
                        type="text" 
                        required
                        className="input-field border-primary-100 focus:border-primary-500" 
                        placeholder="Ej: inversor_02"
                        value={newUsername}
                        onChange={(e) => setNewUsername(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Nombre para Mostrar</label>
                      <input 
                        type="text" 
                        required
                        className="input-field" 
                        placeholder="Ej: David Salvador"
                        value={newDisplayName}
                        onChange={(e) => setNewDisplayName(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2 col-span-1 md:col-span-2">
                      <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Contraseña Inicial</label>
                      <input 
                        type="password" 
                        required
                        className="input-field" 
                        placeholder="••••••••"
                        value={newPass}
                        onChange={(e) => setNewPass(e.target.value)}
                      />
                    </div>
                    <div className="flex items-center gap-3 py-2">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input 
                          type="checkbox" 
                          className="sr-only peer"
                          checked={isAdminNew}
                          onChange={(e) => setIsAdminNew(e.target.checked)}
                        />
                        <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                      <span className="text-xs font-bold text-slate-600 uppercase tracking-widest">Dar permisos de Administrador</span>
                    </div>

                    <div className="col-span-1 md:col-span-2 pt-4">
                      <button 
                        type="submit" 
                        disabled={loading}
                        className="btn btn-primary w-full md:w-auto px-10 py-4 text-[10px] uppercase tracking-widest shadow-lg flex items-center justify-center gap-2"
                      >
                        {loading ? 'Creando...' : <><UserPlus className="w-4 h-4" /> Crear Cuenta de Socio</>}
                      </button>
                    </div>
                 </form>
               </div>

               <div className="p-6 bg-accent-50 rounded-2xl border border-accent-100 flex items-start gap-4">
                 <ShieldAlert className="w-5 h-5 text-accent-600 flex-shrink-0 mt-0.5" />
                 <p className="text-[10px] text-accent-700 font-medium leading-relaxed">
                   <strong>Nota de seguridad:</strong> El registro público ha sido deshabilitado. Como administrador, es responsable de la gestión de credenciales. Los nuevos usuarios deberán cambiar su contraseña tras el primer acceso.
                 </p>
               </div>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};
