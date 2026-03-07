import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import type { WorkspaceState, WorkspaceConfig } from '../types/workspace.types';

const initialState: WorkspaceState = {
  config: null,
  agents: [],
  loading: true,
  error: null,
  refetch: () => {},
};

const WorkspaceContext = createContext<WorkspaceState>(initialState);

export const useWorkspace = () => useContext(WorkspaceContext);

export const WorkspaceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<WorkspaceState>(initialState);

  const loadWorkspace = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const [configRes, agentsRes] = await Promise.all([
        fetch('/api/config'),
        fetch('/api/agents'),
      ]);

      if (!configRes.ok || !agentsRes.ok) {
        throw new Error('Failed to load workspace data');
      }

      const config: WorkspaceConfig = await configRes.json();
      const agentsData = await agentsRes.json();

      setState(prev => ({
        ...prev,
        config,
        agents: agentsData.agents || [],
        loading: false,
        error: null,
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        config: null,
        agents: [],
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to load workspace',
      }));
    }
  }, []);

  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  const value: WorkspaceState = { ...state, refetch: loadWorkspace };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
};
