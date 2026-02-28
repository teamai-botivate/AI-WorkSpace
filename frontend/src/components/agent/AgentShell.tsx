/**
 * Agent Shell — Loads an agent's frontend inside an iframe.
 * For "coming-soon" agents, shows the ComingSoon placeholder instead.
 */

import { useState, useCallback } from "react";
import { ExternalLink, RefreshCw, Maximize2, Minimize2, AlertTriangle } from "lucide-react";
import { ComingSoon } from "@/components/common/ComingSoon";
import { getAgentIcon } from "@/utils/iconMap";
import type { AgentConfig } from "@/types/workspace.types";

interface AgentShellProps {
  agent: AgentConfig;
  onBack: () => void;
}

export function AgentShell({ agent, onBack }: AgentShellProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const Icon = getAgentIcon(agent.icon);

  // If the agent is "coming-soon", show placeholder
  if (agent.status !== "active") {
    return <ComingSoon agent={agent} onBack={onBack} />;
  }

  const iframeUrl = agent.frontend.url;

  const handleLoad = useCallback(() => {
    setLoading(false);
    setError(false);
  }, []);

  const handleError = useCallback(() => {
    setLoading(false);
    setError(true);
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    setError(false);
    const iframe = document.getElementById("agent-iframe") as HTMLIFrameElement;
    if (iframe) {
      iframe.src = iframe.src;
    }
  };

  const handleOpenExternal = () => {
    window.open(iframeUrl, "_blank");
  };

  return (
    <div className={`animate-fade-in ${fullscreen ? "fixed inset-0 z-40 bg-white" : ""}`}>
      {/* Agent Toolbar */}
      <div
        className="flex items-center justify-between px-4 py-2 border-b border-slate-200/60 bg-slate-50/80"
        style={{ borderTop: `2px solid ${agent.gradient[0]}20` }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{
              background: `linear-gradient(135deg, ${agent.gradient[0]}15, ${agent.gradient[1]}15)`,
            }}
          >
            <Icon className="w-3.5 h-3.5" style={{ color: agent.gradient[0] }} />
          </div>
          <div>
            <span className="text-sm font-medium text-slate-700">{agent.name}</span>
            <span className="text-xs text-slate-400 ml-2">
              {(agent.backend.deployed || agent.frontend.deployed) ? (
                <span className="text-emerald-500">Deployed</span>
              ) : (
                <>Port {agent.frontend.port}</>
              )}
            </span>
          </div>
          {loading && (
            <div className="flex items-center gap-1.5 text-xs text-brand-600 animate-pulse-soft">
              <div className="w-1.5 h-1.5 rounded-full bg-brand-500 animate-pulse" />
              Loading...
            </div>
          )}
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleRefresh}
            className="btn-ghost !p-1.5 !rounded-lg"
            title="Refresh"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setFullscreen(!fullscreen)}
            className="btn-ghost !p-1.5 !rounded-lg"
            title={fullscreen ? "Exit fullscreen" : "Fullscreen"}
          >
            {fullscreen ? (
              <Minimize2 className="w-3.5 h-3.5" />
            ) : (
              <Maximize2 className="w-3.5 h-3.5" />
            )}
          </button>
          <button
            onClick={handleOpenExternal}
            className="btn-ghost !p-1.5 !rounded-lg"
            title="Open in new tab"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="flex flex-col items-center justify-center h-[calc(100vh-130px)] gap-4">
          <div className="w-16 h-16 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-red-400" />
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold text-slate-900 mb-1">
              Agent Not Reachable
            </h3>
            <p className="text-sm text-slate-500 mb-1">
              Could not connect to <code className="px-1.5 py-0.5 bg-slate-100 rounded text-xs font-mono">{iframeUrl}</code>
            </p>
            <p className="text-xs text-slate-400 mb-4">
              {agent.backend.deployed
                ? "The deployed service might be starting up. Render free-tier can take ~30s."
                : `Make sure the agent's frontend server is running on port ${agent.frontend.port}`}
            </p>
          </div>
          <div className="flex gap-3">
            <button onClick={handleRefresh} className="btn-primary">
              <RefreshCw className="w-4 h-4" />
              Retry
            </button>
            <button onClick={onBack} className="btn-ghost">
              Back to Dashboard
            </button>
          </div>
        </div>
      )}

      {/* Iframe */}
      <iframe
        id="agent-iframe"
        src={iframeUrl}
        className={`agent-iframe ${error ? "hidden" : ""}`}
        style={{
          height: fullscreen ? "calc(100vh - 48px)" : "calc(100vh - 112px)",
        }}
        onLoad={handleLoad}
        onError={handleError}
        title={agent.name}
        allow="clipboard-read; clipboard-write; microphone; camera"
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals allow-downloads"
      />
    </div>
  );
}
