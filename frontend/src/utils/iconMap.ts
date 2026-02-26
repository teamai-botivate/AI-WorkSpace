/**
 * Icon Map Utility
 * Maps icon name strings from config to Lucide React components.
 * Add new icons here when adding new agents.
 */

import {
  UserSearch,
  Headphones,
  Factory,
  TrendingUp,
  Wrench,
  BarChart3,
  Zap,
  Bot,
  ShoppingCart,
  Truck,
  FileText,
  Shield,
  Brain,
  Settings,
  type LucideIcon,
} from "lucide-react";

const iconMap: Record<string, LucideIcon> = {
  UserSearch,
  Headphones,
  Factory,
  TrendingUp,
  Wrench,
  BarChart3,
  Zap,
  Bot,
  ShoppingCart,
  Truck,
  FileText,
  Shield,
  Brain,
  Settings,
};

export function getAgentIcon(iconName: string): LucideIcon {
  return iconMap[iconName] || Bot;
}
