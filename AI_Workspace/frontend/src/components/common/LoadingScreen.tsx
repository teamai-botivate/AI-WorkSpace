import React from 'react';

const LoadingScreen: React.FC = () => (
  <div className="flex items-center justify-center min-h-screen bg-slate-900">
    <div className="text-center">
      <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-6" />
      <h2 className="text-xl font-semibold text-white mb-2">Loading Workspace</h2>
      <p className="text-slate-400">Connecting to AI agents...</p>
    </div>
  </div>
);

export default LoadingScreen;
