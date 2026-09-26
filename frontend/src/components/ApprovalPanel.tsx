import React, { useState } from 'react';
import { ApprovalItem } from '../types';
import { ShieldAlert, Check, X, Eye, AlertTriangle } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface ApprovalPanelProps {
  approvals: ApprovalItem[];
  onDecide: (actionId: string, approved: boolean, comment?: string) => void;
}

export const ApprovalPanel: React.FC<ApprovalPanelProps> = ({ approvals, onDecide }) => {
  const [selectedItem, setSelectedItem] = useState<ApprovalItem | null>(null);

  if (approvals.length === 0) return null;

  return (
    <div className="bg-amber-950/20 border-2 border-amber-600/60 rounded-2xl p-6 shadow-2xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-amber-800/40">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/20 text-amber-400 rounded-xl border border-amber-500/40">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-amber-200 uppercase tracking-wide">
              ACTION REQUIRES HUMAN APPROVAL
            </h3>
            <p className="text-xs text-amber-300/80">
              The agent has prepared consequential external actions. Review and approve to proceed.
            </p>
          </div>
        </div>
        <StatusBadge status="PENDING_APPROVAL" />
      </div>

      <div className="space-y-4">
        {approvals.map((item) => (
          <div
            key={item.action_id}
            className="bg-slate-950 border border-amber-900/50 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4"
          >
            <div className="space-y-1.5 flex-1">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-amber-400 font-bold">{item.action_id}</span>
                <span className="text-xs font-semibold text-slate-300">[{item.action_type}]</span>
                <span className="text-xs text-rose-400 font-mono px-2 py-0.5 rounded bg-rose-950/40 border border-rose-800/40">
                  Risk: {item.risk_level}
                </span>
              </div>
              <p className="text-sm text-slate-200 font-medium">{item.description}</p>
              <div className="text-xs text-slate-400 flex items-center gap-4">
                <span>Target: <strong className="text-slate-300">{item.target}</strong></span>
                <span>Impact: <strong className="text-slate-300">{item.impact}</strong></span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setSelectedItem(selectedItem?.action_id === item.action_id ? null : item)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700 transition"
              >
                <Eye className="w-3.5 h-3.5" />
                Review Evidence
              </button>

              <button
                onClick={() => onDecide(item.action_id, true)}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold rounded-lg transition shadow-md shadow-emerald-600/20"
              >
                <Check className="w-3.5 h-3.5" />
                Approve
              </button>

              <button
                onClick={() => onDecide(item.action_id, false)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-950/80 hover:bg-rose-900 text-rose-300 text-xs font-semibold rounded-lg border border-rose-800/60 transition"
              >
                <X className="w-3.5 h-3.5" />
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedItem && (
        <div className="mt-3 p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono space-y-2">
          <div className="flex items-center justify-between text-slate-400 font-sans font-bold">
            <span>Evidence Payload Inspection:</span>
            <button onClick={() => setSelectedItem(null)} className="text-slate-500 hover:text-slate-300">Close</button>
          </div>
          <pre className="text-slate-300 overflow-x-auto max-h-48 p-2 bg-slate-900 rounded">
            {JSON.stringify(selectedItem.evidence, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
