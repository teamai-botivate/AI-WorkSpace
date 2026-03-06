/**
 * Header — Top navigation bar.
 * Shows company branding (from config) + agent name when inside an agent.
 */

import { ArrowLeft, RefreshCw, ExternalLink } from "lucide-react";
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
          <div className="flex items-center">
            {selectedAgent ? (
              <div className="flex items-center">
                <button
                  onClick={onBack}
                  className="btn-ghost !p-2 !rounded-lg mr-5"
                  aria-label="Back to dashboard"
                >
                  <ArrowLeft className="w-5 h-5 text-slate-600" />
                </button>
                
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center shadow-sm"
                    style={{
                      background: `linear-gradient(135deg, ${selectedAgent.gradient[0]}, ${selectedAgent.gradient[1]})`,
                    }}
                  >
                    {Icon && <Icon className="w-5 h-5 text-white" />}
                  </div>
                  <div className="flex flex-col">
                    <h1 className="text-[15px] font-semibold text-slate-900 leading-none mb-1">
                      {selectedAgent.name}
                    </h1>
                    <p className="text-[#64748b] text-xs font-medium leading-none">
                      {selectedAgent.category}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-1">
                <img
                  src="/botivate-logo.png"
                  alt="Botivate"
                  className="w-20 h-20 -mr-5 object-contain"
                />
                <div className="flex flex-col">
                  <h1 className="text-lg font-bold text-slate-900 leading-tight tracking-tight">
                    {workspace.name}
                  </h1>
                  <p className="text-xs text-slate-500 leading-tight">
                    {workspace.tagline}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            {!selectedAgent ? (
              <button
                onClick={refreshHealth}
                className="btn-ghost !p-2 !rounded-lg group"
                title="Refresh agent status"
              >
                <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
              </button>
            ) : (
              <>
                <div className="hidden sm:flex items-center mr-2 px-2.5 py-1 rounded-full bg-slate-100 text-xs font-medium text-slate-500">
                  {selectedAgent.backend.deployed ||
                  selectedAgent.frontend.deployed ? (
                    <span className="text-emerald-600 flex items-center gap-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      Deployed
                    </span>
                  ) : (
                    <span>Port {selectedAgent.frontend.port}</span>
                  )}
                </div>
                <button
                  onClick={() => {
                    const iframe = document.getElementById(
                      "agent-iframe",
                    ) as HTMLIFrameElement;
                    if (iframe) iframe.src = iframe.src;
                  }}
                  className="btn-ghost !p-2 !rounded-lg"
                  title="Refresh Agent"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
                <button
                  onClick={() =>
                    window.open(selectedAgent.frontend.url, "_blank")
                  }
                  className="btn-ghost !p-2 !rounded-lg"
                  title="Open in new tab"
                >
                  <ExternalLink className="w-4 h-4" />
                </button>
              </>
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
