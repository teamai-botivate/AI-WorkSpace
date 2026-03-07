import React from 'react';
import { useWorkspace } from '../../context/WorkspaceContext';
import type { AgentInfo } from '../../types/workspace.types';
import AgentCard from './AgentCard';
import { Bot, Zap } from 'lucide-react';

interface DashboardProps {
  onSelectAgent: (agent: AgentInfo) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onSelectAgent }) => {
  const { agents, config, loading, error } = useWorkspace();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center bg-red-500/10 border border-red-500/20 rounded-2xl p-8 max-w-md">
          <p className="text-red-400 font-semibold mb-2">Connection Error</p>
          <p className="text-slate-400 text-sm">{error}</p>
          <p className="text-slate-500 text-xs mt-3">
            Make sure the backend is running on port 8000
          </p>
        </div>
      </div>
    );
  }

  const activeAgents = agents.filter(a => a.status === 'active');
  const otherAgents = agents.filter(a => a.status !== 'active');

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-blue-400" />
          <span className="text-blue-400 text-sm font-medium">AI Workspace</span>
        </div>
        <h2 className="text-3xl font-bold text-white mb-3">
          Welcome to {config?.company?.name || 'Botivate'}
        </h2>
        <p className="text-slate-400 max-w-xl mx-auto">
          {config?.company?.tagline || 'Your unified AI-powered workforce management platform.'}
          {' '}Select an agent below to get started.
        </p>
        <div className="flex items-center justify-center gap-4 mt-6">
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-xl">
            <Bot className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-slate-300">{activeAgents.length} Active Agents</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-xl">
            <span className="text-sm text-slate-300">{agents.length} Total</span>
          </div>
        </div>
      </div>

      {/* Active Agents Grid */}
      {activeAgents.length > 0 && (
        <div className="mb-12">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full" />
            Active Agents
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activeAgents.map((agent) => (
              <AgentCard key={agent.name} agent={agent} onClick={onSelectAgent} />
            ))}
          </div>
        </div>
      )}

      {/* Inactive Agents */}
      {otherAgents.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-slate-400 mb-6 flex items-center gap-2">
            <span className="w-2 h-2 bg-slate-500 rounded-full" />
            Inactive Agents
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {otherAgents.map((agent) => (
              <AgentCard key={agent.name} agent={agent} onClick={() => {}} />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {agents.length === 0 && (
        <div className="text-center py-20">
          <Bot className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-400 mb-2">No Agents Found</h3>
          <p className="text-slate-500 max-w-md mx-auto">
            Add agent plugins to <code className="text-blue-400">backend/app/agents/</code> and restart the server.
          </p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
