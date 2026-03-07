import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ErrorScreenProps {
  message: string;
  onRetry?: () => void;
}

const ErrorScreen: React.FC<ErrorScreenProps> = ({ message, onRetry }) => (
  <div className="flex items-center justify-center min-h-screen bg-slate-900">
    <div className="text-center bg-red-500/10 border border-red-500/20 rounded-2xl p-10 max-w-md">
      <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-white mb-2">Something went wrong</h2>
      <p className="text-slate-400 mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  </div>
);

export default ErrorScreen;
