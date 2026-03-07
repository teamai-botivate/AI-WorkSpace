import React from 'react';
import { useWorkspace } from '../../context/WorkspaceContext';
import { Bot } from 'lucide-react';

interface HeaderProps {
  selectedAgent?: string | null;
  onBack?: () => void;
}

const Header: React.FC<HeaderProps> = ({ selectedAgent, onBack }) => {
  const { config } = useWorkspace();
  const companyName = config?.company?.name || 'Botivate';
  const primaryColor = config?.company?.primaryColor || '#2563eb';

  return (
    <header className="bg-slate-800/50 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          {selectedAgent && onBack && (
            <button
              onClick={onBack}
              className="text-slate-400 hover:text-white transition-colors mr-2"
            >
              ← Back
            </button>
          )}
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: `linear-gradient(135deg, ${primaryColor}, ${primaryColor}dd)` }}
          >
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">{companyName}</h1>
            {!selectedAgent && (
              <p className="text-xs text-slate-400">
                {config?.company?.tagline || 'AI-Powered Workforce Management'}
              </p>
            )}
            {selectedAgent && (
              <p className="text-xs text-blue-400">{selectedAgent}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 bg-green-500/10 text-green-400 text-xs rounded-full border border-green-500/20">
            System Online
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
