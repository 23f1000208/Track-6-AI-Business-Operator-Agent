export interface PaymentRecord {
  payment_id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  amount: number;
  currency: string;
  status: 'COMPLETED' | 'PENDING' | 'FAILED';
  failure_reason?: string;
  created_at: string;
  age_days: number;
  tier: string;
  requires_action: boolean;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  recommended_action?: string;
}

export interface PaymentClassificationSummary {
  total_analyzed: number;
  require_attention: number;
  failed_count: number;
  pending_count: number;
  completed_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  total_at_risk_amount: number;
  affected_customers: string[];
}

export interface AgentStepData {
  step_number: number;
  action: string;
  tool?: string;
  status: 'STARTED' | 'COMPLETED' | 'FAILED' | 'SKIPPED' | 'PAUSED_APPROVAL';
  result_summary: string;
  structured_details?: any;
  timestamp: string;
}

export interface ApprovalItem {
  action_id: string;
  run_id: string;
  action_type: string;
  description: string;
  target: string;
  impact: string;
  risk_level: string;
  evidence: any;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
}

export interface ExecutiveSummary {
  title: string;
  user_request: string;
  payments_analyzed: number;
  require_attention: number;
  failed_count: number;
  pending_count: number;
  total_at_risk_amount: number;
  actions_taken: string[];
  actions_failed: string[];
  verification: string[];
  exceptions: string[];
  workflow_metrics: {
    duration_sec: number;
    tools_used: number;
    actions_executed: number;
    actions_successful: number;
    actions_failed: number;
    human_approvals: number;
    at_risk_exposure: number;
  };
  next_steps: string[];
}

export interface AgentRunState {
  run_id: string;
  user_request: string;
  intent?: string;
  objective?: string;
  plan: string[];
  current_step: number;
  max_steps: number;
  status: 'INITIALIZED' | 'RUNNING' | 'PENDING_APPROVAL' | 'COMPLETED' | 'PARTIAL_SUCCESS' | 'PARTIAL_FAILURE' | 'FAILED' | 'STOPPED';
  retrieved_payments: PaymentRecord[];
  classification_summary?: PaymentClassificationSummary;
  steps: AgentStepData[];
  tool_results: Record<string, any>;
  decisions: string[];
  completed_actions: any[];
  failed_actions: any[];
  pending_approvals: ApprovalItem[];
  verification_results: string[];
  workflow_metrics: Record<string, any>;
  final_result?: ExecutiveSummary;
  error_message?: string;
  is_demo_mode: boolean;
  started_at: string;
  completed_at?: string;
}

export interface IntegrationStatus {
  name: string;
  service_id: string;
  status: 'CONNECTED' | 'DEMO MODE' | 'ERROR' | 'NOT CONFIGURED';
  is_live: boolean;
  capabilities: string[];
  description: string;
}

export interface DashboardStats {
  active_workflows: number;
  pending_actions: number;
  completed_today: number;
  failed_actions: number;
  total_recovered_or_tracked: number;
  integrations_active: number;
  recent_runs: any[];
}
