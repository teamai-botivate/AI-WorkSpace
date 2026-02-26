/**
 * Botivate — Main App Shell
 * Config-driven: reads agents from workspace config, renders dashboard or agent shell.
 */

import { useState } from "react";
import { useWorkspace } from "@/context/WorkspaceContext";
import { Header } from "@/components/layout/Header";
import { Dashboard } from "@/components/dashboard/Dashboard";
import { AgentShell } from "@/components/agent/AgentShell";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { ErrorScreen } from "@/components/common/ErrorScreen";
import type { AgentConfig } from "@/types/workspace.types";

export default function App() {
  const { config, health, loading, error } = useWorkspace();
  const [selectedAgent, setSelectedAgent] = useState<AgentConfig | null>(null);

  if (loading) return <LoadingScreen />;
  if (error || !config) return <ErrorScreen message={error} />;

  const handleSelectAgent = (agent: AgentConfig) => {
    setSelectedAgent(agent);
  };

  const handleBack = () => {
    setSelectedAgent(null);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header
        workspace={config.workspace}
        selectedAgent={selectedAgent}
        onBack={handleBack}
      />
      <main>
        {selectedAgent ? (
          <AgentShell agent={selectedAgent} onBack={handleBack} />
        ) : (
          <Dashboard
            workspace={config.workspace}
            agents={config.agents}
            health={health}
            onSelectAgent={handleSelectAgent}
          />
        )}
      </main>
    </div>
  );
}
