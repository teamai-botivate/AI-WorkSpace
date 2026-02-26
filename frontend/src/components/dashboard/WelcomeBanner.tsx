/**
 * Welcome Banner — Hero section on the dashboard.
 * Renders company name, tagline, and a gradient background.
 */

import { Sparkles } from "lucide-react";
import type { WorkspaceMeta } from "@/types/workspace.types";

interface WelcomeBannerProps {
  workspace: WorkspaceMeta;
  totalAgents: number;
}

export function WelcomeBanner({ workspace, totalAgents }: WelcomeBannerProps) {
  return (
    <div className="animate-fade-in">
      <div
        className="relative overflow-hidden rounded-2xl p-8 sm:p-10"
        style={{
          background: `linear-gradient(135deg, ${workspace.theme.primaryColor}, ${workspace.theme.accentColor})`,
        }}
      >
        {/* Decorative elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div
            className="absolute -top-24 -right-24 w-80 h-80 rounded-full opacity-10"
            style={{ background: "radial-gradient(circle, white 0%, transparent 70%)" }}
          />
          <div
            className="absolute -bottom-32 -left-16 w-64 h-64 rounded-full opacity-10"
            style={{ background: "radial-gradient(circle, white 0%, transparent 70%)" }}
          />
          {/* Grid pattern overlay */}
          <div
            className="absolute inset-0 opacity-5"
            style={{
              backgroundImage:
                "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
              backgroundSize: "32px 32px",
            }}
          />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-3">
            <div className="flex items-center gap-1.5 px-3 py-1 bg-white/15 backdrop-blur-sm rounded-full border border-white/20">
              <Sparkles className="w-3.5 h-3.5 text-white/90" />
              <span className="text-xs font-medium text-white/90">
                {totalAgents} AI Agents Registered
              </span>
            </div>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold text-white mb-2 tracking-tight">
            Welcome to {workspace.name}
          </h1>
          <p className="text-base sm:text-lg text-white/80 max-w-xl">
            {workspace.tagline}. Select an AI agent below to get started.
          </p>
        </div>
      </div>
    </div>
  );
}
