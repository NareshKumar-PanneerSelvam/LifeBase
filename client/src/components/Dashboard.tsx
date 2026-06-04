import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';
import { Shield, LogOut } from 'lucide-react';
import { modulesConfig } from '../config/modulesConfig';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'checking'>('checking');

  const apiBase = api.defaults.baseURL || '';
  const apiHost = apiBase.startsWith('http') ? new URL(apiBase).host : window.location.host;

  // Verify server status on mount
  useEffect(() => {
    const checkServer = async () => {
      try {
        await api.get('/health');
        setServerStatus('online');
      } catch (err) {
        setServerStatus('offline');
      }
    };
    checkServer();
  }, []);

  const handleLogoutClick = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans animate-fade-in">
      {/* Thin Sidebar */}
      <aside className="w-16 flex flex-col items-center bg-slate-900/60 border-r border-slate-900 py-4 z-40 select-none">
        
        {/* Top Avatar with Info Tooltip */}
        <div className="relative group pb-4 flex items-center justify-center border-b border-slate-800/50 w-full">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-emerald-500 flex items-center justify-center text-white font-bold text-sm shadow-md cursor-pointer hover:scale-105 transition-transform duration-200">
              {user?.full_name ? user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'AD'}
            </div>
            
            {/* Pulsing Status Dot */}
            <span className={`absolute bottom-0 right-0 block h-2.5 w-2.5 rounded-full ring-2 ring-slate-950 ${serverStatus === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          </div>

          {/* User Popover Panel on Hover */}
          <div className="absolute left-full ml-3 p-3 bg-slate-900/95 backdrop-blur-md border border-slate-800 text-slate-100 text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 shadow-xl min-w-[200px] space-y-2">
            <div className="font-semibold text-slate-200">{user?.full_name}</div>
            <div className="text-slate-400 text-[10px] truncate">{user?.email}</div>
            <div className="border-t border-slate-800 my-1 pt-1 text-[10px] text-indigo-400 font-mono">
              Role: {user?.role || 'USER'}
            </div>
          </div>
        </div>

        {/* Dynamic Sidebar Icons with Tooltips */}
        <nav className="flex-1 flex flex-col items-center gap-4 py-6 w-full overflow-y-auto">
          {modulesConfig.map((module) => {
            const IconComponent = module.icon;
            // Check active routing
            const isActive = location.pathname === `/dashboard/${module.route}` || 
                             (module.route === '' && location.pathname === '/dashboard');
            return (
              <div key={module.id} className="relative group w-full flex items-center justify-center">
                {/* Active Indicator Bar */}
                {isActive && (
                  <div className="absolute left-0 w-1 h-8 bg-indigo-500 rounded-r-md" />
                )}

                <NavLink
                  to={module.route === '' ? '/dashboard' : `/dashboard/${module.route}`}
                  end={module.route === ''}
                  className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-200 ${isActive ? 'text-indigo-400 bg-indigo-500/10' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}`}
                >
                  <IconComponent size={20} />
                </NavLink>

                {/* Tooltip */}
                <div className="absolute left-full ml-3 px-2 py-1 bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 shadow-md">
                  {module.name}
                </div>
              </div>
            );
          })}
        </nav>

        {/* Bottom Logout Button */}
        <div className="relative group py-4 flex items-center justify-center border-t border-slate-800/50 w-full mt-auto">
          <button 
            onClick={handleLogoutClick} 
            className="w-10 h-10 rounded-lg flex items-center justify-center text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors duration-200"
          >
            <LogOut size={20} />
          </button>

          {/* Tooltip */}
          <div className="absolute left-full ml-3 px-2 py-1 bg-slate-900 border border-slate-800 text-rose-450 text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 shadow-md">
            Logout Session
          </div>
        </div>

      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-950/20">
        
        {/* Sleek Top Header Bar */}
        <header className="h-14 border-b border-slate-900 flex items-center justify-between px-6 bg-slate-900/10 backdrop-blur-sm z-30">
          <div className="flex items-center gap-2">
            <Shield size={18} className="text-indigo-500" />
            <span className="text-sm font-semibold tracking-wider uppercase text-slate-200">LifeBase Admin</span>
            <span className="text-[10px] text-slate-450 px-2 py-0.5 rounded bg-slate-900 border border-slate-850 font-mono">
              SECURE
            </span>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-slate-450">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
              <span>Host: {apiHost}</span>
            </div>
            
            <div className="flex items-center gap-1.5 text-slate-450">
              <span>Server Status:</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${serverStatus === 'online' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                {serverStatus.toUpperCase()}
              </span>
            </div>
          </div>
        </header>

        {/* Dynamic Router Outlet */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-950">
          <div className="max-w-6xl mx-auto w-full h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
