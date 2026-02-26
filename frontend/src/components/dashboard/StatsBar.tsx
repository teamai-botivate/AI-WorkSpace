/**
 * Stats Bar — Quick overview of system health.
 */

import { Activity, CheckCircle2, AlertCircle, Server } from "lucide-react";
import type { AllAgentsHealth } from "@/types/workspace.types";

interface StatsBarProps {
  health: AllAgentsHealth | null;
  totalAgents: number;
}

export function StatsBar({ health, totalAgents }: StatsBarProps) {
  const stats = [
    {
      label: "Total Agents",
      value: totalAgents,
      icon: Server,
      color: "text-brand-600",
      bg: "bg-brand-50",
      border: "border-brand-100",
    },
    {
      label: "Online",
      value: health?.healthy ?? "—",
      icon: CheckCircle2,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      border: "border-emerald-100",
    },
    {
      label: "Offline",
      value: health ? health.total - health.healthy : "—",
      icon: AlertCircle,
      color: "text-red-500",
      bg: "bg-red-50",
      border: "border-red-100",
    },
    {
      label: "System",
      value: health && health.healthy > 0 ? "Operational" : "—",
      icon: Activity,
      color: "text-amber-600",
      bg: "bg-amber-50",
      border: "border-amber-100",
    },
  ];

  return (
    <div
      className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up"
      style={{ animationDelay: "0.1s", animationFillMode: "both" }}
    >
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={`card px-5 py-4 flex items-center gap-4 ${stat.border}`}
        >
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${stat.bg}`}>
            <stat.icon className={`w-5 h-5 ${stat.color}`} />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">{stat.label}</p>
            <p className="text-lg font-bold text-slate-900 leading-tight">
              {stat.value}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
