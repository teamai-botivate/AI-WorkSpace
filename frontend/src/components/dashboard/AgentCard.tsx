/**
 * Agent Card — Displays a single agent on the dashboard.
 * Fully dynamic: icon, colors, features, status — all from config.
 */

import { ArrowRight, Circle } from "lucide-react";
import { getAgentIcon } from "@/utils/iconMap";
import type { AgentConfig, AgentHealthStatus } from "@/types/workspace.types";

interface AgentCardProps {
  agent: AgentConfig;
  health?: AgentHealthStatus;
  onClick: () => void;
  index: number;
  dimmed?: boolean;
}

export function AgentCard({ agent, health, onClick, index, dimmed }: AgentCardProps) {
  const Icon = getAgentIcon(agent.icon);
  const isOnline = health?.healthy ?? false;

  return (
    <div
      onClick={onClick}
      className={`card-interactive group p-6 ${dimmed ? "opacity-60" : ""}`}
      style={{
        animationDelay: `${index * 0.08}s`,
        animationFillMode: "both",
      }}
    >
      {/* Top Row: Icon + Status */}
      <div className="flex items-start justify-between mb-4">
        <div
          className="icon-gradient group-hover:scale-110 transition-transform duration-300"
          style={{
            background: `linear-gradient(135deg, ${agent.gradient[0]}, ${agent.gradient[1]})`,
          }}
        >
          <Icon className="w-6 h-6 text-white" />
        </div>

        <div className="flex items-center gap-1.5">
          {agent.status === "active" ? (
            <>
              <Circle
                className={`w-2 h-2 fill-current ${
                  isOnline ? "text-emerald-500" : "text-slate-300"
                }`}
                style={
                  isOnline
                    ? { filter: "drop-shadow(0 0 4px rgba(16, 185, 129, 0.5))" }
                    : undefined
                }
              />
              <span className={`text-xs font-medium ${isOnline ? "text-emerald-600" : "text-slate-400"}`}>
                {isOnline ? "Online" : "Offline"}
              </span>
            </>
          ) : (
            <span className="text-xs font-medium text-amber-500 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
              Soon
            </span>
          )}
        </div>
      </div>

      {/* Name + Description */}
      <h3 className="text-base font-semibold text-slate-900 mb-1 group-hover:text-brand-700 transition-colors">
        {agent.name}
      </h3>
      <p className="text-sm text-slate-500 leading-relaxed mb-4">
        {agent.description}
      </p>

      {/* Feature Pills */}
      <div className="flex flex-wrap gap-1.5 mb-5">
        {agent.features.slice(0, 4).map((feature) => (
          <span
            key={feature}
            className="feature-pill group-hover:bg-brand-50 group-hover:text-brand-700 group-hover:border-brand-200"
          >
            {feature}
          </span>
        ))}
      </div>

      {/* CTA */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
        <span className="text-xs text-slate-400 font-medium">{agent.category}</span>
        <div
          className="flex items-center gap-1.5 text-sm font-semibold transition-all duration-300 group-hover:gap-2.5"
          style={{ color: agent.gradient[0] }}
        >
          Launch
          <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-0.5" />
        </div>
      </div>
    </div>
  );
}
