import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { Cpu, ShieldCheck, Database, Key, Layers } from 'lucide-react';

export const OverviewModule: React.FC = () => {
  const { user, token } = useAuth();
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'checking'>('checking');

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

  const truncateToken = (tokenStr: string | null) => {
    if (!tokenStr) return 'No token';
    return `${tokenStr.substring(0, 14)}...${tokenStr.substring(tokenStr.length - 14)}`;
  };

  return (
    <div className="animate-slide-up space-y-6">
      <div className="p-6 rounded-lg bg-slate-900/40 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Hello, {user?.full_name || 'Administrator'}!</h1>
          <p className="text-slate-400 mt-1">Welcome to your LifeBase security workspace dashboard.</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800 flex items-center justify-between">
          <div className="space-y-2">
            <h4 className="text-slate-400 text-sm font-medium">Security Shield</h4>
            <div className="flex items-center gap-2">
              <ShieldCheck size={20} className="text-indigo-400 animate-pulse" />
              <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded text-xs font-semibold">JWT Active</span>
            </div>
          </div>
          <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-lg">
            <Key size={20} />
          </div>
        </div>

        <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800 flex items-center justify-between">
          <div className="space-y-2">
            <h4 className="text-slate-400 text-sm font-medium">Database Migrations</h4>
            <div className="flex items-center gap-2">
              <Database size={20} className="text-emerald-400 animate-pulse" />
              <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded text-xs font-semibold">Alembic Active</span>
            </div>
          </div>
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <Database size={20} />
          </div>
        </div>

        <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800 flex items-center justify-between">
          <div className="space-y-2">
            <h4 className="text-slate-400 text-sm font-medium">Active User Role</h4>
            <p className="text-lg font-semibold text-indigo-400">
              {user?.role || 'ROLE_USER'}
            </p>
          </div>
          <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-lg">
            <Layers size={20} />
          </div>
        </div>
      </div>

      {/* Grid detail */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800 space-y-4">
          <h2 className="flex items-center gap-2 text-lg font-bold text-slate-100">
            <Cpu size={20} className="text-indigo-400" />
            Architecture Overview
          </h2>
          <div className="text-slate-300 text-sm leading-relaxed space-y-3">
            <p>
              This environment successfully couples a <strong>React (Vite)</strong> frontend with a 
              highly configured <strong>FastAPI</strong> security core. 
            </p>
            <p>
              All API queries are intercepted by the client's network broker, extracting the stored JWT token
              and feeding it securely inside the Authorization header. On the server, a custom 
              security pipeline decodes and validates credentials against your persistent PostgreSQL database before letting
              the route handler respond.
            </p>
            <p>
              Use the sidebar links to navigate through the modules and developers' console!
            </p>
          </div>
        </div>

        <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800 space-y-4">
          <h2 className="text-lg font-bold text-slate-100">Connection Parameters</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-slate-400 text-sm">Active JWT Session Token</span>
              <span className="text-indigo-400 text-xs font-mono bg-indigo-500/10 px-2 py-0.5 rounded">{truncateToken(token)}</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-slate-400 text-sm">Database Management</span>
              <span className="text-slate-200 text-sm">Alembic versioned migrations</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-slate-400 text-sm">Persistence Type</span>
              <span className="text-slate-200 text-sm">SQLAlchemy / Asyncpg / PostgreSQL</span>
            </div>
            <div className="flex justify-between items-center pt-1">
              <span className="text-slate-400 text-sm">Server Broker Status</span>
              <span className={`px-2 py-0.5 rounded text-xs ${serverStatus === 'online' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                {serverStatus}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewModule;
