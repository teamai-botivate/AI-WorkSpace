/**
 * Botivate Workspace — Type Definitions
 * All types are derived from workspace.config.json schema.
 * No hardcoding — everything is config-driven.
 */

export interface WorkspaceTheme {
  primaryColor: string;
  accentColor: string;
  mode: "light" | "dark";
}

export interface WorkspaceMeta {
  name: string;
  tagline: string;
  version: string;
  theme: WorkspaceTheme;
}

export interface AgentBackendConfig {
  port: number;
  healthCheck: string;
  startCommand: string;
  workDir: string;
  envFile?: string;
  activateVenv?: string;
}

export interface AgentFrontendConfig {
  port: number;
  url: string;
  type: "vite" | "static" | "next";
  startCommand: string;
  workDir: string;
  env?: Record<string, string>;
}

export interface AgentConfig {
  id: string;
  name: string;
  description: string;
  icon: string;
  gradient: [string, string];
  status: "active" | "coming-soon" | "disabled";
  category: string;
  features: string[];
  backend: AgentBackendConfig;
  frontend: AgentFrontendConfig;
}

export interface GatewayConfig {
  port: number;
  corsOrigins: string[];
}

export interface WorkspaceConfig {
  workspace: WorkspaceMeta;
  gateway: GatewayConfig;
  agents: AgentConfig[];
}

export interface AgentHealthStatus {
  agent_id: string;
  name?: string;
  healthy: boolean;
  status: "running" | "offline" | "error";
  port: number;
}

export interface AllAgentsHealth {
  total: number;
  healthy: number;
  agents: AgentHealthStatus[];
}
