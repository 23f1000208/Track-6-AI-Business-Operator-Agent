import React from 'react';
import { AgentStepData } from '../types';
import {
  CheckCircle2, Clock, AlertCircle, ShieldAlert, Cpu,
  Search, ListTodo, Mail, MessageSquare, BookOpen, Layers
} from 'lucide-react';

interface WorkflowTimelineProps {
  steps: AgentStepData[];
  currentStatus: string;
}

const getActionIcon = (action: string, tool?: string) => {
  if (tool) {
    const t = tool.toLowerCase();
    if (t.includes('paypal')) return Search;
    if (t.includes('jira')) return ListTodo;
    if (t.includes('gmail')) return Mail;
    if (t.includes('slack')) return MessageSquare;
    if (t.includes('notion')) return BookOpen;
  }
  if (action === 'SECURITY_SCAN') return ShieldAlert;
  if (action === 'UNDERSTAND' || action === 'PLAN') return Cpu;
  if (action === 'APPLY_BUSINESS_RULES') return Layers;
  return CheckCircle2;
};

export const WorkflowTimeline: React.FC<WorkflowTimelineProps> = ({ steps, currentStatus }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
        <div>
          <h3 className="text-base font-bold text-white tracking-wide flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-sky-400" />
            LIVE AGENT WORKFLOW TIMELINE
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time multi-step state transitions driven by Google ADK orchestration
          </p>
        </div>
        <div className="text-xs font-mono px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-slate-400">
          Steps Recorded: <span className="text-sky-400 font-bold">{steps.length}</span>
        </div>
      </div>

      {steps.length === 0 ? (
        <div className="text-center py-12 text-slate-500 text-sm">
          No workflow active. Submit a command or click "Run 2-Minute Demo" to begin execution.
        </div>
      ) : (
        <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
          {steps.map((step, idx) => {
            const IconComponent = getActionIcon(step.action, step.tool);
            const isCompleted = step.status === 'COMPLETED';
            const isFailed = step.status === 'FAILED';
            const isPaused = step.status === 'PAUSED_APPROVAL';

            let iconBg = 'bg-slate-800 text-slate-400 border-slate-700';
            if (isCompleted) iconBg = 'bg-emerald-950 text-emerald-400 border-emerald-700';
            if (isFailed) iconBg = 'bg-rose-950 text-rose-400 border-rose-700';
            if (isPaused) iconBg = 'bg-amber-950 text-amber-400 border-amber-700';

            return (
              <div key={idx} className="relative group">
                <div className={`absolute -left-6 top-1 p-1 rounded-full border ${iconBg} shadow-sm`}>
                  <IconComponent className="w-3.5 h-3.5" />
                </div>

                <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-4 hover:border-slate-700 transition">
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-sky-400">
                        Step {step.step_number}: {step.action}
                      </span>
                      {step.tool && (
                        <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">
                          {step.tool}
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(step.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  <p className="text-sm text-slate-300 leading-relaxed font-sans">
                    {step.result_summary}
                  </p>

                  {step.structured_details && Object.keys(step.structured_details).length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-slate-900 flex flex-wrap gap-2 text-xs">
                      {step.structured_details.hash && (
                        <span className="font-mono text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded">
                          SHA256: {step.structured_details.hash.slice(0, 12)}...
                        </span>
                      )}
                      {step.structured_details.total_analyzed !== undefined && (
                        <span className="text-xs text-slate-400 bg-slate-900 px-2 py-0.5 rounded">
                          Analyzed: <strong className="text-slate-200">{step.structured_details.total_analyzed}</strong> |
                          At-Risk: <strong className="text-amber-400">{step.structured_details.require_attention}</strong>
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
