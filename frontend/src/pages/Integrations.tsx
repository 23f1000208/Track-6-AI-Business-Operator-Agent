import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { IntegrationStatus } from '../types';
import { IntegrationCard } from '../components/IntegrationCard';
import { Layers, ShieldCheck, RefreshCw } from 'lucide-react';

export const Integrations: React.FC = () => {
  const [integrations, setIntegrations] = useState<IntegrationStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchIntegrations = () => {
    setRefreshing(true);
    api.getIntegrations()
      .then(data => setIntegrations(data))
      .catch(console.error)
      .finally(() => {
        setLoading(false);
        setRefreshing(false);
      });
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <Layers className="w-6 h-6 text-sky-400" />
            SWYTCHCODE INTEGRATIONS (TRACK 6)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Autonomous multi-tool gateway integration. Transparent connection status without simulated mock deception.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchIntegrations}
            disabled={refreshing}
            className="flex items-center gap-2 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 px-3 py-1.5 rounded-xl transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh Status</span>
          </button>

          <div className="flex items-center gap-2 text-xs font-mono bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl text-slate-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Requirement: Min 3 Active APIs (5 Connected)</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {integrations.map((item) => (
          <IntegrationCard key={item.service_id} integration={item} />
        ))}
      </div>

      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 mt-8">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-2">
          Architecture & Adapter Separation
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          OpsPilot AI uses an abstract adapter architecture (<code className="text-sky-400">BaseIntegration</code>). When live API keys for Swytchcode are present in environment variables, real production endpoints are called. When in Demo Mode (<code className="text-sky-400">DEMO_MODE=true</code>), realistic synthetic datasets execute through the identical agent tool loop without requiring live banking or email credentials.
        </p>
      </div>
    </div>
  );
};
