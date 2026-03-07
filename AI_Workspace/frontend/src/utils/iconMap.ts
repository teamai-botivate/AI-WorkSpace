import {
  Headphones,
  UserSearch,
  Bot,
  Shield,
  Brain,
  FileText,
  Mail,
  Settings,
  BarChart3,
  Calendar,
  Users,
  Briefcase,
  type LucideIcon,
} from 'lucide-react';

const iconMap: Record<string, LucideIcon> = {
  Headphones,
  UserSearch,
  Bot,
  Shield,
  Brain,
  FileText,
  Mail,
  Settings,
  BarChart3,
  Calendar,
  Users,
  Briefcase,
};

export const getIcon = (name: string): LucideIcon => {
  return iconMap[name] || Bot;
};
