import React from 'react';
import { ExecutiveSummary, PaymentClassificationSummary } from '../types';
import { CheckCircle, AlertTriangle, ShieldCheck, Clock, Tool, Activity, ArrowRight } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface ResultSummaryProps {
  summary: ExecutiveSummary;
  classification?: PaymentClassificationSummary;
}

export const ResultSummary: React.FC<ResultSummaryProps> = ({ summary, classification }) => {
  const metrics = summary.workflow_metrics || {};

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-full bg-emerald-500/20 text-emerald-400">
              <CheckCircle className="w-5 h-5" />
            </span>
            <h3 className="text-lg font-bold text-white tracking-wide">{summary.title}</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Prompt: <span className="text-slate-300 italic">"{summary.user_request}"</span>
          </p>
        </div>
        <StatusBadge status="COMPLETED" />
      </div>

      {/* Numerical Classification Ground Truth (ZERO LLM ARITHMETIC) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Payments Analyzed</p>
          <p className="text-2xl font-bold text-white mt-1">{summary.payments_analyzed}</p>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-amber-400">Require Attention</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">{summary.require_attention}</p>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-rose-400">Failed / Pending SLA</p>
          <p className="text-2xl font-bold text-rose-400 mt-1">
            {summary.failed_count} <span className="text-xs text-slate-500 font-normal">/ {summary.pending_count}</span>
          </p>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-emerald-400">Total At-Risk Exposure</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1">
            ${summary.total_at_risk_amount ? summary.total_at_risk_amount.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '0.00'}
          </p>
        </div>
      </div>

      {/* Actions and Verifications Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Actions Taken */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-sky-400" />
            Actions Executed & Verified
          </h4>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2.5 max-h-56 overflow-y-auto">
            {summary.actions_taken.map((action, i) => (
              <div key={i} className="text-xs text-emerald-300 flex items-start gap-2">
                <span className="text-emerald-400 font-bold shrink-0 mt-0.5">✓</span>
                <span className="text-slate-300 font-medium">{action.replace('✓ ', '')}</span>
              </div>
            ))}
            {summary.actions_failed && summary.actions_failed.map((fail, i) => (
              <div key={i} className="text-xs text-rose-400 flex items-start gap-2">
                <span className="text-rose-400 font-bold shrink-0 mt-0.5">✗</span>
                <span className="font-medium">{fail}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Multi-System Verification Audit */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Verification Evidence (Requirement 23)
          </h4>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2.5 max-h-56 overflow-y-auto">
            {summary.verification.map((verif, i) => (
              <div key={i} className="text-xs text-slate-300 flex items-start gap-2">
                <span className="text-emerald-400 font-bold shrink-0 mt-0.5">✓</span>
                <span className="font-mono text-[11px]">{verif}</span>
              </div>
            ))}
            {summary.verification.length === 0 && (
              <p className="text-xs text-slate-500">No external mutations to verify.</p>
            )}
          </div>
        </div>
      </div>

      {/* Measured Business Impact Metrics (Requirement 36) */}
      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-sky-400" />
          <span className="text-slate-400">Duration:</span>
          <strong className="text-white font-mono">{metrics.duration_sec ?? 0}s</strong>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Tools Used:</span>
          <strong className="text-sky-400 font-mono">{metrics.tools_used ?? 0}</strong>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Actions Executed:</span>
          <strong className="text-emerald-400 font-mono">{metrics.actions_executed ?? 0}</strong>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Approvals:</span>
          <strong className="text-amber-400 font-mono">{metrics.human_approvals ?? 0}</strong>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Exceptions:</span>
          <strong className="text-slate-300 font-mono">{summary.exceptions?.length ?? 0}</strong>
        </div>
      </div>
    </div>
  );
};
