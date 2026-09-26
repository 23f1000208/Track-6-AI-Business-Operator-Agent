import React from 'react';
import { IntegrationStatus } from '../types';
import { StatusBadge } from './StatusBadge';
import { CreditCard, Mail, MessageSquare, ListTodo, BookOpen, Check } from 'lucide-react';

interface IntegrationCardProps {
  integration: IntegrationStatus;
}

const getServiceIcon = (id: string) => {
  switch (id.toLowerCase()) {
    case 'stripe': return CreditCard;
    case 'paypal': return CreditCard;
    case 'gmail': return Mail;
    case 'slack': return MessageSquare;
    case 'jira': return ListTodo;
    case 'notion': return BookOpen;
    default: return Check;
  }
};

export const IntegrationCard: React.FC<IntegrationCardProps> = ({ integration }) => {
  const Icon = getServiceIcon(integration.service_id);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-slate-700 transition flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-slate-800 text-sky-400 border border-slate-700">
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-base font-bold text-white tracking-wide">{integration.name}</h4>
              <span className="text-[10px] text-slate-500 font-mono uppercase">Track 6 Adapter</span>
            </div>
          </div>
          <StatusBadge status={integration.status} />
        </div>

        <p className="text-xs text-slate-400 leading-relaxed mb-4">
          {integration.description}
        </p>
      </div>

      <div className="pt-3 border-t border-slate-800/80">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2 block">
          Registered Capabilities
        </span>
        <div className="flex flex-wrap gap-1.5">
          {integration.capabilities.map((cap, i) => (
            <span
              key={i}
              className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800"
            >
              {cap}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
