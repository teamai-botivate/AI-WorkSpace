/**
 * Header — Top navigation bar.
 * Shows company branding (from config) + agent name when inside an agent.
 */

import { ArrowLeft, RefreshCw } from "lucide-react";
import { useWorkspace } from "@/context/WorkspaceContext";
import type { WorkspaceMeta, AgentConfig } from "@/types/workspace.types";
import { getAgentIcon } from "@/utils/iconMap";

interface HeaderProps {
  workspace: WorkspaceMeta;
  selectedAgent: AgentConfig | null;
  onBack: () => void;
}

export function Header({ workspace, selectedAgent, onBack }: HeaderProps) {
  const { refreshHealth } = useWorkspace();
  const Icon = selectedAgent ? getAgentIcon(selectedAgent.icon) : null;

  return (
    <header className="sticky top-0 z-50 glass-strong border-b border-slate-200/60">
      {/* Gradient accent line */}
      <div
        className="h-0.5 w-full"
        style={{
          background: selectedAgent
            ? `linear-gradient(90deg, ${selectedAgent.gradient[0]}, ${selectedAgent.gradient[1]})`
            : `linear-gradient(90deg, ${workspace.theme.primaryColor}, ${workspace.theme.accentColor})`,
        }}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left: Logo + Title */}
          <div className="flex items-center gap-1">
            {selectedAgent ? (
              <>
                <button
                  onClick={onBack}
                  className="btn-ghost !p-2 !rounded-lg"
                  aria-label="Back to dashboard"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <div className="h-6 w-px bg-slate-200" />
                <div
                  className="icon-gradient w-9 h-9"
                  style={{
                    background: `linear-gradient(135deg, ${selectedAgent.gradient[0]}, ${selectedAgent.gradient[1]})`,
                  }}
                >
                  {Icon && <Icon className="w-4 h-4 text-white" />}
                </div>
                <div>
                  <h1 className="text-sm font-semibold text-slate-900 leading-tight">
                    {selectedAgent.name}
                  </h1>
                  <p className="text-xs text-slate-500">{selectedAgent.category}</p>
                </div>
              </>
            ) : (
              <>
                <img
                  src="/botivate-logo.png"
                  alt="Botivate"
                  className="w-20 h-20 -mr-5 object-contain"
                />
                <div>
                  <h1 className="text-lg font-bold text-slate-900 leading-tight tracking-tight">
                    {workspace.name}
                  </h1>
                  <p className="text-xs text-slate-500 leading-tight">
                    {workspace.tagline}
                  </p>
                </div>
              </>
            )}
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            {!selectedAgent && (
              <button
                onClick={refreshHealth}
                className="btn-ghost !p-2 !rounded-lg group"
                title="Refresh agent status"
              >
                <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
              </button>
            )}
            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <span className="text-xs text-slate-400 font-medium">
                v{workspace.version}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
