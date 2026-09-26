import { AgentRunState, DashboardStats, IntegrationStatus, ApprovalItem } from '../types';

const API_BASE = '/api';

export const api = {
  async getDashboard(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard`);
    if (!res.ok) throw new Error('Failed to load dashboard metrics');
    return res.json();
  },

  async getIntegrations(): Promise<IntegrationStatus[]> {
    const res = await fetch(`${API_BASE}/integrations?_t=${Date.now()}`, {
      cache: 'no-store',
      headers: { 'Pragma': 'no-cache', 'Cache-Control': 'no-cache' }
    });
    if (!res.ok) throw new Error('Failed to load integrations');
    return res.json();
  },

  async getActivity(limit: number = 50): Promise<any[]> {
    const res = await fetch(`${API_BASE}/activity?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to load activity log');
    return res.json();
  },

  async getApprovals(): Promise<ApprovalItem[]> {
    const res = await fetch(`${API_BASE}/approvals`);
    if (!res.ok) throw new Error('Failed to load approvals');
    return res.json();
  },

  async decideApproval(actionId: string, approved: boolean, comment?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/approvals/${actionId}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved, approved_by: 'business_operator', comment })
    });
    if (!res.ok) throw new Error('Failed to submit approval decision');
    return res.json();
  },

  async runAgent(prompt: string, requireApproval: boolean = false, simulateFailure: boolean = false): Promise<AgentRunState> {
    const res = await fetch(`${API_BASE}/agent/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        require_approval: requireApproval,
        demo_mode: true,
        simulate_failure: simulateFailure
      })
    });
    if (!res.ok) throw new Error('Failed to execute agent run');
    return res.json();
  },

  async runPrimaryDemo(): Promise<AgentRunState> {
    const res = await fetch(`${API_BASE}/demo/run-quick`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to run primary demo');
    return res.json();
  },

  async runFailureSimulation(): Promise<AgentRunState> {
    const res = await fetch(`${API_BASE}/demo/simulate-failure`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to run failure simulation');
    return res.json();
  },

  streamRun(prompt: string, onEvent: (event: any) => void): EventSource {
    const url = `${API_BASE}/agent/runs/stream?prompt=${encodeURIComponent(prompt)}`;
    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onEvent(data);
        if (data.type === 'RUN_COMPLETED') {
          eventSource.close();
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      eventSource.close();
    };

    return eventSource;
  }
};
