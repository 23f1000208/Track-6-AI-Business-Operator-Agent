import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AgentRunState, DashboardStats, ApprovalItem } from '../types';
import { MetricsCard } from '../components/MetricsCard';
import { AgentCommandBox } from '../components/AgentCommandBox';
import { WorkflowTimeline } from '../components/WorkflowTimeline';
import { AgentTrace } from '../components/AgentTrace';
import { ApprovalPanel } from '../components/ApprovalPanel';
import { ResultSummary } from '../components/ResultSummary';
import { Activity, Clock, AlertCircle, CheckCircle2, ShieldAlert, DollarSign } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [currentState, setCurrentState] = useState<AgentRunState | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [dash, apps] = await Promise.all([
        api.getDashboard(),
        api.getApprovals()
      ]);
      setStats(dash);
      setApprovals(apps);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleRun = (prompt: string, requireApproval: boolean, simulateFailure: boolean) => {
    setIsRunning(true);
    setError(null);
    setCurrentState(null);

    // Use SSE Streaming for real-time live execution
    api.streamRun(prompt, (event) => {
      if (event.type === 'STEP_UPDATE') {
        setCurrentState(event.state);
        if (event.state.pending_approvals) {
          setApprovals(event.state.pending_approvals);
        }
      } else if (event.type === 'RUN_COMPLETED') {
        setCurrentState(event.state);
        setIsRunning(false);
        loadData();
      }
    });
  };

  const handleQuickDemo = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const result = await api.runPrimaryDemo();
      setCurrentState(result);
      loadData();
    } catch (err: any) {
      setError(err.message || 'Demo run failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleApprovalDecision = async (actionId: string, approved: boolean, comment?: string) => {
    try {
      await api.decideApproval(actionId, approved, comment);
      setApprovals(prev => prev.filter(a => a.action_id !== actionId));
      loadData();
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      {/* KPI Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          label="Active Workflows"
          value={isRunning ? 1 : (stats?.active_workflows ?? 0)}
          subtext="Google ADK Orchestrated"
          icon={Activity}
          variant="sky"
        />
        <MetricsCard
          label="Pending Actions"
          value={approvals.length || (stats?.pending_actions ?? 0)}
          subtext="Human Sign-off Required"
          icon={ShieldAlert}
          variant={approvals.length > 0 ? 'amber' : 'emerald'}
        />
        <MetricsCard
          label="Completed Today"
          value={stats?.completed_today ?? 3}
          subtext="Autonomous Operations"
          icon={CheckCircle2}
          variant="emerald"
        />
        <MetricsCard
          label="Total At-Risk Tracked"
          value={`$${(stats?.total_recovered_or_tracked ?? 1710).toLocaleString()}`}
          subtext="Zero LLM Arithmetic"
          icon={DollarSign}
          variant="indigo"
        />
      </div>

      {/* Main Command Center */}
      <AgentCommandBox
        onRun={handleRun}
        onQuickDemo={handleQuickDemo}
        isRunning={isRunning}
      />

      {/* Human Approval Required Panel */}
      <ApprovalPanel
        approvals={approvals}
        onDecide={handleApprovalDecision}
      />

      {/* Final Executive Summary Panel (When workflow finishes) */}
      {currentState?.final_result && (
        <ResultSummary
          summary={currentState.final_result}
          classification={currentState.classification_summary}
        />
      )}

      {/* Live Workflow Timeline and Safe Agent Trace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <WorkflowTimeline
            steps={currentState?.steps ?? []}
            currentStatus={currentState?.status ?? 'IDLE'}
          />
        </div>
        <div>
          <AgentTrace
            steps={currentState?.steps ?? []}
            intent={currentState?.intent}
            objective={currentState?.objective}
            decisions={currentState?.decisions ?? []}
          />
        </div>
      </div>
    </div>
  );
};
