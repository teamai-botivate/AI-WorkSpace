/**
 * Agent Shell — Loads an agent's frontend inside an iframe.
 * For "coming-soon" agents, shows the ComingSoon placeholder instead.
 */

import { useState, useCallback } from "react";
import { RefreshCw, AlertTriangle } from "lucide-react";
import type { AgentConfig } from "@/types/workspace.types";
import { ComingSoon } from "@/components/common/ComingSoon";

interface AgentShellProps {
  agent: AgentConfig;
  onBack: () => void;
}

export function AgentShell({ agent, onBack }: AgentShellProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

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



  return (
    <div className="relative animate-fade-in flex flex-col h-full w-full">
      {/* Loading Bar */}
      {loading && !error && (
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-brand-500 animate-[pulse_1.5s_ease-in-out_infinite] z-50 shadow-[0_0_8px_rgba(var(--brand-500),0.5)]" />
      )}      {/* Error State */}
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
          height: "calc(100vh - 64px)",
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
