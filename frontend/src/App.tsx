import React, { useState } from 'react';
import { Dashboard } from './pages/Dashboard';
import { Integrations } from './pages/Integrations';
import { ActivityPage } from './pages/Activity';
import { SettingsPage } from './pages/SettingsPage';
import { LayoutDashboard, Layers, History, Settings, Zap, Shield, Sparkles } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'integrations' | 'activity' | 'settings'>('dashboard');

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
              <Zap className="w-5 h-5 fill-current" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-extrabold text-white tracking-wide">OPSPILOT AI</h1>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-sky-950 text-sky-400 border border-sky-800">
                  Track 6
                </span>
              </div>
              <p className="text-[11px] text-slate-400 tracking-tight">
                "From Business Intent to Autonomous Execution."
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'dashboard'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              Command Center
            </button>
            <button
              onClick={() => setActiveTab('integrations')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'integrations'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              Integrations (5)
            </button>
            <button
              onClick={() => setActiveTab('activity')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'activity'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              Audit Trail
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'settings'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Settings className="w-3.5 h-3.5" />
              Architecture
            </button>
          </nav>

          {/* Right Mode Badges */}
          <div className="flex items-center gap-2.5">
            <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-emerald-950/80 text-emerald-300 border border-emerald-800/80">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Google ADK Active
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-semibold bg-indigo-950 text-indigo-300 border border-indigo-800">
              DEMO MODE
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'integrations' && <Integrations />}
        {activeTab === 'activity' && <ActivityPage />}
        {activeTab === 'settings' && <SettingsPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500 font-sans">
        <p>
          OpsPilot AI — Build with Swytchcode (Gurgaon Edition) • Track 6: AI Business Operator Agent
        </p>
        <p className="text-[11px] text-slate-600 mt-1">
          Google ADK (Orchestration) → Gemini (Interpretation) → Python (Deterministic Ground Truth) → Swytchcode (Business Execution)
        </p>
      </footer>
    </div>
  );
};

export default App;
