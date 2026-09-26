import React from 'react';
import { Shield, Key, Lock, Cpu, Server, Check } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div className="pb-4 border-b border-slate-800">
        <h2 className="text-xl font-bold text-white tracking-wide">
          SYSTEM SETTINGS & SECURITY ARCHITECTURE
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Configuration parameters, defense-in-depth security layers, and execution rules.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2.5 text-sky-400">
            <Cpu className="w-5 h-5" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">Google ADK & Gemini Engine</h3>
          </div>
          <div className="space-y-2 text-xs text-slate-300 leading-relaxed">
            <p><strong>Framework:</strong> Google ADK (<code className="text-sky-300">google-adk 2.9.2</code>)</p>
            <p><strong>Model:</strong> Gemini 2.5 Flash (<code className="text-sky-300">google-genai</code>)</p>
            <p><strong>Separation of Responsibility:</strong></p>
            <ul className="list-disc pl-5 space-y-1 text-slate-400">
              <li>Google ADK: Tool coordination, agent loop, and state management</li>
              <li>Gemini: Natural language understanding & qualitative summarization</li>
              <li>Python: Deterministic classification & Zero LLM Arithmetic</li>
            </ul>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2.5 text-emerald-400">
            <Lock className="w-5 h-5" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">Secret Isolation & Scrubbing</h3>
          </div>
          <div className="space-y-2 text-xs text-slate-300 leading-relaxed">
            <p><strong>Isolation Status:</strong> <span className="text-emerald-400 font-semibold">Active & Enforced</span></p>
            <p className="text-slate-400">
              No API keys or tokens are ever placed inside prompts, agent state, SQLite database logs, or transmitted to the browser UI. All credentials reside strictly in server-side environment variables.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
        <div className="flex items-center gap-2.5 text-amber-400">
          <Shield className="w-5 h-5" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white">Execution Safety Limits</h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center">
            <span className="text-slate-500 block text-[10px]">MAX_AGENT_STEPS</span>
            <span className="text-white font-bold text-sm">25 Steps</span>
          </div>
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center">
            <span className="text-slate-500 block text-[10px]">MAX_TOOL_RETRIES</span>
            <span className="text-white font-bold text-sm">3 Retries</span>
          </div>
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center">
            <span className="text-slate-500 block text-[10px]">TOOL_TIMEOUT</span>
            <span className="text-white font-bold text-sm">30 Seconds</span>
          </div>
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center">
            <span className="text-slate-500 block text-[10px]">WORKFLOW_TIMEOUT</span>
            <span className="text-white font-bold text-sm">180 Seconds</span>
          </div>
        </div>
      </div>
    </div>
  );
};
