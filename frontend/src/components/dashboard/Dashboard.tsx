/**
 * Dashboard — Main landing page.
 * Renders welcome banner, stats, and agent cards grid — all from config.
 */

import { WelcomeBanner } from "./WelcomeBanner";
import { StatsBar } from "./StatsBar";
import { AgentCard } from "./AgentCard";
import type {
  WorkspaceMeta,
  AgentConfig,
  AllAgentsHealth,
} from "@/types/workspace.types";

interface DashboardProps {
  workspace: WorkspaceMeta;
  agents: AgentConfig[];
  health: AllAgentsHealth | null;
  onSelectAgent: (agent: AgentConfig) => void;
}

export function Dashboard({
  workspace,
  agents,
  health,
  onSelectAgent,
}: DashboardProps) {
  const activeAgents = agents.filter((a) => a.status === "active");
  const comingSoonAgents = agents.filter((a) => a.status === "coming-soon");

  const getAgentHealth = (agentId: string) => {
    if (!health) return undefined;
    return health.agents.find((h) => h.agent_id === agentId);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Banner */}
      <WelcomeBanner workspace={workspace} totalAgents={agents.length} />

      {/* Stats Bar */}
      <StatsBar health={health} totalAgents={agents.length} />

      {/* Active Agents */}
      {activeAgents.length > 0 && (
        <section className="animate-slide-up" style={{ animationDelay: "0.2s", animationFillMode: "both" }}>
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-xl font-bold text-slate-900">AI Agents</h2>
              <p className="text-sm text-slate-500 mt-0.5">
                Select an agent to launch its workspace
              </p>
            </div>
            <span className="text-xs font-medium text-slate-400 bg-slate-100 px-3 py-1 rounded-full">
              {activeAgents.length} active
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {activeAgents.map((agent, index) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                health={getAgentHealth(agent.id)}
                onClick={() => onSelectAgent(agent)}
                index={index}
              />
            ))}
          </div>
        </section>
      )}

      {/* Coming Soon Agents */}
      {comingSoonAgents.length > 0 && (
        <section className="animate-slide-up" style={{ animationDelay: "0.4s", animationFillMode: "both" }}>
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Coming Soon</h2>
              <p className="text-sm text-slate-500 mt-0.5">
                These agents are being developed
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {comingSoonAgents.map((agent, index) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                onClick={() => onSelectAgent(agent)}
                index={index}
                dimmed
              />
            ))}
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="text-center py-6 border-t border-slate-200/60">
        <p className="text-xs text-slate-400">
          {workspace.name} v{workspace.version} — AI-Powered Workforce Management
        </p>
      </footer>
    </div>
  );
}
