import { useQuery } from '@tanstack/react-query';
import { Activity, Clock, AlertTriangle, CheckSquare, FileText, Calendar } from 'lucide-react';
import { dashboardApi } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LoadingPage } from '@/components/ui/loading-spinner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

export default function AnalystWorkbenchPage() {
  const { data: analystData, isLoading, error } = useQuery({
    queryKey: ['dashboard', 'analyst-workbench'],
    queryFn: dashboardApi.getAnalystWorkbench,
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
            Failed to load analyst workbench data. Please try refreshing the page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Activity className="h-8 w-8" />
            Analyst Workbench
          </h1>
          <p className="text-muted-foreground">
            Your tactical workload manager and assessment center
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline">
            <Calendar className="w-4 h-4 mr-2" />
            Schedule Assessment
          </Button>
          <Button>
            <CheckSquare className="w-4 h-4 mr-2" />
            New Task
          </Button>
        </div>
      </div>

      {/* Workload Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">My Open Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">2 due today</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Overdue Items</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">3</div>
            <p className="text-xs text-muted-foreground">Require immediate attention</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">5</div>
            <p className="text-xs text-muted-foreground">Awaiting your review</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">This Week's Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">73%</div>
            <Progress value={73} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Workbench */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* My Open Tasks */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckSquare className="h-5 w-5" />
              My Open Tasks
            </CardTitle>
            <CardDescription>Tasks assigned to you</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex-1">
                <p className="font-medium text-sm">Review firewall configuration</p>
                <p className="text-xs text-muted-foreground">Due: Today</p>
              </div>
              <Badge variant="destructive" className="text-xs">Critical</Badge>
            </div>
            
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex-1">
                <p className="font-medium text-sm">Complete NIST assessment</p>
                <p className="text-xs text-muted-foreground">Due: Tomorrow</p>
              </div>
              <Badge className="bg-orange-100 text-orange-800 text-xs">High</Badge>
            </div>
            
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex-1">
                <p className="font-medium text-sm">Update risk register</p>
                <p className="text-xs text-muted-foreground">Due: Friday</p>
              </div>
              <Badge variant="secondary" className="text-xs">Medium</Badge>
            </div>
            
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex-1">
                <p className="font-medium text-sm">Evidence review - IAM controls</p>
                <p className="text-xs text-muted-foreground">Due: Next week</p>
              </div>
              <Badge variant="secondary" className="text-xs">Medium</Badge>
            </div>
            
            <Button variant="outline" className="w-full" size="sm">
              View All Tasks
            </Button>
          </CardContent>
        </Card>
        
        {/* Upcoming Assessments */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Upcoming Assessments
            </CardTitle>
            <CardDescription>Scheduled assessment activities</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3 border rounded-lg">
              <p className="font-medium text-sm">HR Systems - NIST CSF</p>
              <p className="text-xs text-muted-foreground">Scheduled: July 15, 2025</p>
              <p className="text-xs text-blue-600">In Progress (65% complete)</p>
              <Progress value={65} className="mt-2 h-1" />
            </div>
            
            <div className="p-3 border rounded-lg">
              <p className="font-medium text-sm">Production Network - CIS Controls</p>
              <p className="text-xs text-muted-foreground">Scheduled: July 20, 2025</p>
              <p className="text-xs text-muted-foreground">Status: Draft</p>
            </div>
            
            <div className="p-3 border rounded-lg">
              <p className="font-medium text-sm">Cloud Infrastructure - SOC 2</p>
              <p className="text-xs text-muted-foreground">Scheduled: July 25, 2025</p>
              <p className="text-xs text-muted-foreground">Status: Planning</p>
            </div>
            
            <Button variant="outline" className="w-full" size="sm">
              View Assessment Calendar
            </Button>
          </CardContent>
        </Card>
        
        {/* Recent High-Risk Findings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Recent High-Risk Findings
            </CardTitle>
            <CardDescription>Latest critical findings from integrations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3 border rounded-lg border-red-200">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-red-500 rounded-full" />
                <p className="font-medium text-sm">CVE-2024-1234</p>
                <Badge variant="destructive" className="text-xs">Critical</Badge>
              </div>
              <p className="text-xs text-muted-foreground">Remote code execution in web server</p>
              <p className="text-xs text-blue-600">Detected 2 hours ago</p>
            </div>
            
            <div className="p-3 border rounded-lg border-orange-200">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-orange-500 rounded-full" />
                <p className="font-medium text-sm">Unauthorized access attempt</p>
                <Badge className="bg-orange-100 text-orange-800 text-xs">High</Badge>
              </div>
              <p className="text-xs text-muted-foreground">Multiple failed login attempts detected</p>
              <p className="text-xs text-blue-600">Detected 1 day ago</p>
            </div>
            
            <div className="p-3 border rounded-lg border-orange-200">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-orange-500 rounded-full" />
                <p className="font-medium text-sm">Misconfigured S3 bucket</p>
                <Badge className="bg-orange-100 text-orange-800 text-xs">High</Badge>
              </div>
              <p className="text-xs text-muted-foreground">Public read access enabled</p>
              <p className="text-xs text-blue-600">Detected 2 days ago</p>
            </div>
            
            <Button variant="outline" className="w-full" size="sm">
              View All Findings
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Evidence Awaiting Review */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Evidence Awaiting Review
          </CardTitle>
          <CardDescription>Documents and evidence requiring your analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">Password Policy v2.1</p>
                  <p className="text-sm text-muted-foreground">Uploaded by John Smith • 2 days ago</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">Policy Document</Badge>
                <Button size="sm" variant="outline">Review</Button>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">Firewall Configuration Screenshot</p>
                  <p className="text-sm text-muted-foreground">Uploaded by Mike Johnson • 1 day ago</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">Screenshot</Badge>
                <Button size="sm" variant="outline">Review</Button>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">Security Training Certificate</p>
                  <p className="text-sm text-muted-foreground">Uploaded by Sarah Wilson • 3 hours ago</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">Certificate</Badge>
                <Button size="sm" variant="outline">Review</Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}