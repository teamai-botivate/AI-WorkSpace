import React from 'react';
import type { AgentInfo } from '../../types/workspace.types';
import { getIcon } from '../../utils/iconMap';

interface AgentCardProps {
  agent: AgentInfo;
  onClick: (agent: AgentInfo) => void;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, onClick }) => {
  const Icon = getIcon(agent.icon);
  const isActive = agent.status === 'active';
  const gradient = agent.gradient || ['#6366f1', '#4f46e5'];

  return (
    <div
      className={`
        relative group rounded-2xl border overflow-hidden transition-all duration-300
        ${isActive
          ? 'border-slate-700/50 hover:border-slate-600 cursor-pointer hover:scale-[1.02] hover:shadow-2xl'
          : 'border-slate-800 opacity-60 cursor-not-allowed'
        }
        bg-slate-800/30 backdrop-blur-sm
      `}
      onClick={() => isActive && onClick(agent)}
    >
      {/* Gradient Header */}
      <div
        className="h-2"
        style={{ background: `linear-gradient(90deg, ${gradient[0]}, ${gradient[1]})` }}
      />

      <div className="p-6">
        {/* Icon + Status */}
        <div className="flex items-start justify-between mb-4">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center"
            style={{ background: `linear-gradient(135deg, ${gradient[0]}20, ${gradient[1]}20)` }}
          >
            <Icon
              className="w-6 h-6"
              style={{ color: gradient[0] }}
            />
          </div>
          <span
            className={`px-2 py-1 text-xs rounded-full ${
              isActive
                ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                : agent.status === 'disabled'
                ? 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }`}
          >
            {agent.status === 'active' ? 'Active' :
             agent.status === 'disabled' ? 'Disabled' :
             agent.status === 'missing_credentials' ? 'Missing Keys' : 'Error'}
          </span>
        </div>

        {/* Name + Description */}
        <h3 className="text-lg font-semibold text-white mb-2">{agent.display_name}</h3>
        <p className="text-sm text-slate-400 mb-4 line-clamp-2">{agent.description}</p>

        {/* Features */}
        <div className="flex flex-wrap gap-1.5">
          {agent.features?.slice(0, 4).map((feature) => (
            <span
              key={feature}
              className="px-2 py-0.5 text-xs bg-slate-700/50 text-slate-300 rounded-md"
            >
              {feature}
            </span>
          ))}
        </div>

        {/* Version */}
        <div className="mt-4 pt-3 border-t border-slate-700/30 flex items-center justify-between">
          <span className="text-xs text-slate-500">v{agent.version}</span>
          <span className="text-xs text-slate-500">{agent.category}</span>
        </div>
      </div>
    </div>
  );
};

export default AgentCard;
