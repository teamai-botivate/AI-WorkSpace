/**
 * Workspace Types — TypeScript interfaces for the unified AI workspace
 */

export interface CompanyConfig {
  name: string;
  tagline?: string;
  logo?: string;
  favicon?: string;
  primaryColor: string;
  accentColor?: string;
  mode?: 'light' | 'dark';
}

export interface AgentInfo {
  name: string;
  display_name: string;
  status: 'active' | 'disabled' | 'missing_credentials' | 'error';
  version: string;
  description: string;
  icon: string;
  gradient: [string, string];
  category: string;
  features: string[];
  api_prefix?: string;
  error?: string;
  missing_keys?: string[];
}

export interface AgentsResponse {
  agents: AgentInfo[];
  total: number;
  active: number;
}

export interface WorkspaceConfig {
  company: CompanyConfig;
  features: Record<string, boolean>;
  setup_completed: boolean;
}

export interface WorkspaceState {
  config: WorkspaceConfig | null;
  agents: AgentInfo[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}
