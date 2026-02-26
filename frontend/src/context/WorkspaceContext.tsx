/**
 * Workspace Context
 * Provides workspace config to the entire app via React Context.
 * Fetches config from the Gateway API on mount.
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { WorkspaceConfig, AllAgentsHealth } from "@/types/workspace.types";

interface WorkspaceContextValue {
  config: WorkspaceConfig | null;
  health: AllAgentsHealth | null;
  loading: boolean;
  error: string | null;
  refreshHealth: () => Promise<void>;
  refreshConfig: () => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

const GATEWAY_URL = "/api";

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<WorkspaceConfig | null>(null);
  const [health, setHealth] = useState<AllAgentsHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchConfig = async () => {
    try {
      const res = await fetch(`${GATEWAY_URL}/config`);
      if (!res.ok) throw new Error(`Gateway returned ${res.status}`);
      const data: WorkspaceConfig = await res.json();
      setConfig(data);
      setError(null);
    } catch (err) {
      console.error("[Workspace] Failed to fetch config:", err);
      // Fallback: load from static config
      try {
        const fallback = await fetch("/workspace.config.json");
        if (fallback.ok) {
          const data: WorkspaceConfig = await fallback.json();
          setConfig(data);
          setError(null);
          return;
        }
      } catch {}
      setError("Could not connect to the gateway. Make sure the backend is running.");
    }
  };

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${GATEWAY_URL}/agents/health/all`);
      if (!res.ok) return;
      const data: AllAgentsHealth = await res.json();
      setHealth(data);
    } catch {
      // Health check is optional — don't block the UI
    }
  };

  const refreshConfig = async () => {
    await fetchConfig();
  };

  const refreshHealth = async () => {
    await fetchHealth();
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await fetchConfig();
      await fetchHealth();
      setLoading(false);
    };
    init();

    // Poll health every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <WorkspaceContext.Provider
      value={{ config, health, loading, error, refreshHealth, refreshConfig }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace(): WorkspaceContextValue {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return ctx;
}
