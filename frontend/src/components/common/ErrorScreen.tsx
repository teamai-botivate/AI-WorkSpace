/**
 * Error Screen — shown when gateway is unreachable.
 */

import { AlertTriangle, RefreshCw } from "lucide-react";

interface ErrorScreenProps {
  message?: string | null;
}

export function ErrorScreen({ message }: ErrorScreenProps) {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="text-center max-w-md animate-fade-in">
        <div className="w-16 h-16 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center mx-auto mb-6">
          <AlertTriangle className="w-8 h-8 text-red-500" />
        </div>
        <h2 className="text-xl font-semibold text-slate-900 mb-2">
          Connection Failed
        </h2>
        <p className="text-sm text-slate-500 mb-6 leading-relaxed">
          {message || "Could not connect to the workspace gateway. Please ensure all services are running."}
        </p>
        <div className="space-y-3">
          <button
            onClick={() => window.location.reload()}
            className="btn-primary w-full"
          >
            <RefreshCw className="w-4 h-4" />
            Retry Connection
          </button>
          <div className="text-xs text-slate-400 space-y-1">
            <p>Run <code className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-600 font-mono">.\start-dev.ps1</code> to start all services</p>
          </div>
        </div>
      </div>
    </div>
  );
}
