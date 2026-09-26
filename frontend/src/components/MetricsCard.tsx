import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricsCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  variant?: 'sky' | 'emerald' | 'amber' | 'rose' | 'indigo';
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  label,
  value,
  subtext,
  icon: Icon,
  variant = 'sky'
}) => {
  const colorMap = {
    sky: 'text-sky-400 bg-sky-950/40 border-sky-800/40',
    emerald: 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40',
    amber: 'text-amber-400 bg-amber-950/40 border-amber-800/40',
    rose: 'text-rose-400 bg-rose-950/40 border-rose-800/40',
    indigo: 'text-indigo-400 bg-indigo-950/40 border-indigo-800/40',
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm hover:border-slate-700 transition">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</p>
        <div className={`p-2 rounded-lg border ${colorMap[variant]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3">
        <h3 className="text-2xl font-bold text-white tracking-tight">{value}</h3>
        {subtext && <p className="text-xs text-slate-500 mt-1">{subtext}</p>}
      </div>
    </div>
  );
};
