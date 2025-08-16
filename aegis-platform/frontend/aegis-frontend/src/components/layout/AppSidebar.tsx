import {
  BarChart3,
  Shield,
  AlertTriangle,
  CheckSquare,
  FileText,
  Database,
  Settings,
  Users,
  Brain,
  Zap,
  Home,
  Target,
  Activity,
  Inbox,
  Server,
  TrendingUp,
  GitBranch,
  Play,
  History,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { hasPermission, hasRole } from '@/lib/auth';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
} from '@/components/ui/sidebar';
import { Badge } from '@/components/ui/badge';
import { useLocation } from 'react-router-dom';

interface NavItem {
  title: string;
  url: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
  permission?: { module: string; action: string };
  role?: string;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

export function AppSidebar() {
  const { user } = useAuth();
  const location = useLocation();

  const navigationGroups: NavGroup[] = [
    {
      title: "Dashboards",
      items: [
        {
          title: "Overview",
          url: "/dashboard",
          icon: Home,
        },
        {
          title: "CISO Cockpit",
          url: "/dashboard/ciso",
          icon: Target,
          role: "admin",
        },
        {
          title: "Analyst Workbench",
          url: "/dashboard/analyst",
          icon: Activity,
          permission: { module: "assessments", action: "read" },
        },
        {
          title: "System Owner Inbox",
          url: "/dashboard/system-owner",
          icon: Inbox,
        },
      ],
    },
    {
      title: "Risk Management",
      items: [
        {
          title: "Assets",
          url: "/assets",
          icon: Database,
          permission: { module: "assets", action: "read" },
        },
        {
          title: "Risks",
          url: "/risks",
          icon: AlertTriangle,
          badge: 5,
          permission: { module: "risks", action: "read" },
        },
        {
          title: "Assessments",
          url: "/assessments",
          icon: Shield,
          permission: { module: "assessments", action: "read" },
        },
        {
          title: "Tasks",
          url: "/tasks",
          icon: CheckSquare,
          badge: 12,
          permission: { module: "tasks", action: "read" },
        },
      ],
    },
    {
      title: "Documentation",
      items: [
        {
          title: "Evidence",
          url: "/evidence",
          icon: FileText,
          permission: { module: "evidence", action: "read" },
        },
        {
          title: "Reports",
          url: "/reports",
          icon: BarChart3,
          permission: { module: "reports", action: "read" },
        },
      ],
    },
    {
      title: "AI Management",
      items: [
        {
          title: "AI Providers",
          url: "/ai/providers",
          icon: Server,
          permission: { module: "ai_services", action: "read" },
        },
        {
          title: "AI Analytics",
          url: "/ai/analytics",
          icon: TrendingUp,
          permission: { module: "ai_services", action: "read" },
        },
        {
          title: "Predictive Analytics",
          url: "/ai/predictive",
          icon: Brain,
          permission: { module: "ai_services", action: "read" },
        },
      ],
    },
    {
      title: "Workflow Management",
      items: [
        {
          title: "Workflows",
          url: "/workflows",
          icon: GitBranch,
          permission: { module: "workflows", action: "read" },
        },
        {
          title: "Active Instances",
          url: "/workflows/instances",
          icon: Play,
          permission: { module: "workflows", action: "read" },
        },
      ],
    },
    {
      title: "Configuration",
      items: [
        {
          title: "Integrations",
          url: "/integrations",
          icon: Zap,
          permission: { module: "integrations", action: "read" },
        },
        {
          title: "Users",
          url: "/users",
          icon: Users,
          permission: { module: "users", action: "read" },
        },
        {
          title: "Audit Trail",
          url: "/audit",
          icon: History,
          permission: { module: "audit", action: "read" },
        },
        {
          title: "Settings",
          url: "/settings",
          icon: Settings,
        },
      ],
    },
  ];

  const hasAccess = (item: NavItem): boolean => {
    if (item.role && !hasRole(user, item.role)) {
      return false;
    }
    if (item.permission && !hasPermission(user, `${item.permission.module}_${item.permission.action}`)) {
      return false;
    }
    return true;
  };

  const isActive = (url: string): boolean => {
    if (url === '/dashboard' && location.pathname === '/dashboard') {
      return true;
    }
    if (url !== '/dashboard' && location.pathname.startsWith(url)) {
      return true;
    }
    return false;
  };

  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <a href="/dashboard" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg">Aegis</h1>
            <p className="text-xs text-muted-foreground">Risk Management</p>
          </div>
        </a>
      </SidebarHeader>

      <SidebarContent>
        {navigationGroups.map((group) => {
          const visibleItems = group.items.filter(hasAccess);
          
          if (visibleItems.length === 0) {
            return null;
          }

          return (
            <SidebarGroup key={group.title}>
              <SidebarGroupLabel>{group.title}</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {visibleItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={isActive(item.url)}
                      >
                        <a href={item.url} className="flex items-center gap-2">
                          <item.icon className="w-4 h-4" />
                          <span>{item.title}</span>
                          {item.badge && (
                            <Badge variant="secondary" className="ml-auto">
                              {item.badge}
                            </Badge>
                          )}
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          );
        })}
      </SidebarContent>

      <SidebarFooter className="p-4">
        <div className="text-xs text-muted-foreground text-center">
          <p>Aegis Risk Platform</p>
          <p>v1.0.0</p>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}