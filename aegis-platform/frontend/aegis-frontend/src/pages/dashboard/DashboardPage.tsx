import { useQuery } from '@tanstack/react-query';
import { BarChart3, Shield, AlertTriangle, CheckSquare, Database, TrendingUp, Users, Clock } from 'lucide-react';
import { dashboardApi } from '@/lib/api';
import { DashboardMetrics } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LoadingPage } from '@/components/ui/loading-spinner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { hasRole } from '@/lib/auth';

export default function DashboardPage() {
  const { user } = useAuth();
  
  const { data: metrics, isLoading, error } = useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: dashboardApi.getOverview,
  });

  if (isLoading) {
    return <LoadingPage />;
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Failed to load dashboard data. Please try refreshing the page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const dashboardMetrics = metrics as DashboardMetrics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.full_name}. Here's your security posture overview.
          </p>
        </div>
        
        <div className="flex gap-2">
          {hasRole(user, 'admin') && (
            <Button variant="outline" asChild>
              <a href="/dashboard/ciso">
                <BarChart3 className="w-4 h-4 mr-2" />
                CISO Cockpit
              </a>
            </Button>
          )}
          <Button variant="outline" asChild>
            <a href="/dashboard/analyst">
              <Shield className="w-4 h-4 mr-2" />
              Analyst Workbench
            </a>
          </Button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardMetrics.assets.total}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-red-600">{dashboardMetrics.assets.critical}</span> critical assets
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Risks</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardMetrics.risks.total}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-red-600">{dashboardMetrics.risks.high_priority}</span> high priority
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Tasks</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardMetrics.tasks.open}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-orange-600">{dashboardMetrics.tasks.overdue}</span> overdue
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Assessments</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardMetrics.assessments.completed}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardMetrics.assessments.active} in progress
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Risk Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Risk Posture Trend</CardTitle>
            <CardDescription>
              Your organization's risk posture over the last 6 months
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Risk trend chart will be displayed here</p>
                <p className="text-sm">Connect to view detailed analytics</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Recent Alerts</CardTitle>
            <CardDescription>
              Latest security alerts and findings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full" />
                <span className="text-sm">Critical vulnerability detected</span>
              </div>
              <Badge variant="destructive" className="text-xs">New</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full" />
                <span className="text-sm">Task overdue: Firewall review</span>
              </div>
              <Badge variant="secondary" className="text-xs">2d</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-sm">Assessment completed</span>
              </div>
              <Badge variant="secondary" className="text-xs">1w</Badge>
            </div>
            
            <Button variant="outline" className="w-full mt-4" size="sm">
              View All Alerts
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and quick access to key features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Button variant="outline" className="h-20 flex-col" asChild>
              <a href="/assets">
                <Database className="h-6 w-6 mb-2" />
                <span>Manage Assets</span>
              </a>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col" asChild>
              <a href="/risks">
                <AlertTriangle className="h-6 w-6 mb-2" />
                <span>Review Risks</span>
              </a>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col" asChild>
              <a href="/assessments">
                <Shield className="h-6 w-6 mb-2" />
                <span>New Assessment</span>
              </a>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col" asChild>
              <a href="/reports">
                <BarChart3 className="h-6 w-6 mb-2" />
                <span>Generate Report</span>
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}