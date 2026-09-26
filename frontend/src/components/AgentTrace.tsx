import React from 'react';
import { AgentStepData } from '../types';
import { Terminal, Shield, ArrowRight, Check, AlertCircle } from 'lucide-react';

interface AgentTraceProps {
  steps: AgentStepData[];
  intent?: string;
  objective?: string;
  decisions: string[];
}

export const AgentTrace: React.FC<AgentTraceProps> = ({ steps, intent, objective, decisions }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-bold text-white tracking-wider uppercase">SAFE AGENT TRACE</h3>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/60 px-2.5 py-0.5 rounded-full border border-emerald-800/40">
          <Shield className="w-3 h-3" />
          <span>Sanitized Stream</span>
        </div>
      </div>

      {intent && (
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3.5 space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Classified Intent</span>
          <div className="text-xs font-mono text-sky-400 font-bold">{intent}</div>
          {objective && <div className="text-xs text-slate-300 pt-1">{objective}</div>}
        </div>
      )}

      <div className="space-y-3 font-mono text-xs">
        {decisions.map((decision, idx) => (
          <div key={idx} className="bg-slate-950 p-3 rounded-xl border border-slate-800/80 flex items-start gap-2.5">
            <span className="text-amber-400 font-bold shrink-0 mt-0.5">DECISION:</span>
            <span className="text-slate-300">{decision}</span>
          </div>
        ))}

        {steps.filter(s => s.action === 'OBSERVE').map((step, idx) => (
          <div key={idx} className="bg-slate-950 p-3 rounded-xl border border-slate-850 flex items-start gap-2.5">
            <span className="text-sky-400 font-bold shrink-0 mt-0.5">OBSERVED:</span>
            <div className="space-y-1 text-slate-300">
              <span className="text-indigo-300 font-semibold">[{step.tool}]</span> {step.result_summary}
            </div>
          </div>
        ))}

        {decisions.length === 0 && steps.length === 0 && (
          <div className="text-slate-500 py-6 text-center font-sans text-xs">
            Agent trace will stream live operational decisions and observations here.
          </div>
        )}
      </div>
    </div>
  );
};
