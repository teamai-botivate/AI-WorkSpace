/**
 * Coming Soon — placeholder for agents not yet built.
 */

import { Clock, ArrowLeft } from "lucide-react";
import { getAgentIcon } from "@/utils/iconMap";
import type { AgentConfig } from "@/types/workspace.types";

interface ComingSoonProps {
  agent: AgentConfig;
  onBack: () => void;
}

export function ComingSoon({ agent, onBack }: ComingSoonProps) {
  const Icon = getAgentIcon(agent.icon);

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-65px)] p-6">
      <div className="text-center max-w-md animate-scale-in">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 opacity-60"
          style={{
            background: `linear-gradient(135deg, ${agent.gradient[0]}20, ${agent.gradient[1]}20)`,
            border: `1px solid ${agent.gradient[0]}30`,
          }}
        >
          <Icon className="w-10 h-10" style={{ color: agent.gradient[0] }} />
        </div>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-700 text-xs font-medium mb-4">
          <Clock className="w-3 h-3" />
          Coming Soon
        </div>

        <h2 className="text-2xl font-bold text-slate-900 mb-2">{agent.name}</h2>
        <p className="text-sm text-slate-500 mb-2">{agent.description}</p>
        <p className="text-xs text-slate-400 mb-8">
          This agent is being developed and will be available in a future update.
        </p>

        <button onClick={onBack} className="btn-ghost">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>
      </div>
    </div>
  );
}
