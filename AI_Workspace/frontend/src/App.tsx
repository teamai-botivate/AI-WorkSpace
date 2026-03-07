import React, { useState, lazy, Suspense } from 'react';
import Header from './components/layout/Header';
import Dashboard from './components/dashboard/Dashboard';
import LoadingScreen from './components/common/LoadingScreen';
import SetupWizard from './components/setup/SetupWizard';
import { useWorkspace } from './context/WorkspaceContext';
import type { AgentInfo } from './types/workspace.types';

// Lazy-load agent pages — only downloaded when user navigates to them
const HRSupportPage = lazy(() => import('./agents/hr_support/index'));
const ResumeScreeningPage = lazy(() => import('./agents/resume_screening/index'));

const agentPageMap: Record<string, React.LazyExoticComponent<React.FC>> = {
  hr_support: HRSupportPage,
  resume_screening: ResumeScreeningPage,
};

const AgentView: React.FC<{ agentName: string; displayName: string; onBack: () => void }> = ({
  agentName,
  displayName,
  onBack,
}) => {
  const AgentPage = agentPageMap[agentName];

  if (!AgentPage) {
    return (
      <div className="min-h-screen bg-slate-900">
        <Header selectedAgent={displayName} onBack={onBack} />
        <div className="flex items-center justify-center min-h-[70vh]">
          <div className="text-center">
            <p className="text-slate-400">No frontend page found for this agent.</p>
            <p className="text-slate-500 text-sm mt-2">
              Add a page at <code className="text-blue-400">frontend/src/agents/{agentName}/index.tsx</code>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Header selectedAgent={displayName} onBack={onBack} />
      <div className="p-6">
        <Suspense fallback={<LoadingScreen />}>
          <AgentPage />
        </Suspense>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<AgentInfo | null>(null);
  const { config, loading } = useWorkspace();

  const handleSelectAgent = (agent: AgentInfo) => {
    setSelectedAgent(agent);
  };

  const handleBack = () => {
    setSelectedAgent(null);
  };

  // Show loading while fetching config
  if (loading) {
    return <LoadingScreen />;
  }

  // Show setup wizard if company hasn't been configured yet
  if (config && !config.setup_completed) {
    return <SetupWizard />;
  }

  if (selectedAgent) {
    return (
      <AgentView
        agentName={selectedAgent.name}
        displayName={selectedAgent.display_name}
        onBack={handleBack}
      />
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />
      <Dashboard onSelectAgent={handleSelectAgent} />
    </div>
  );
};

export default App;
