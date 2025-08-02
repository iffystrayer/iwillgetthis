import { useQuery } from '@tanstack/react-query';
import { BarChart3, TrendingUp, AlertTriangle, Shield, Target } from 'lucide-react';
import { dashboardApi } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LoadingPage } from '@/components/ui/loading-spinner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

export default function CisoCockpitPage() {
  const { data: cisoDashboard, isLoading, error } = useQuery({
    queryKey: ['dashboard', 'ciso-cockpit'],
    queryFn: dashboardApi.getCisoCockpit,
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
            Failed to load CISO dashboard data. Please try refreshing the page.
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
            <Target className="h-8 w-8" />
            CISO Cockpit
          </h1>
          <p className="text-muted-foreground">
            Executive-level security posture and strategic risk insights
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline">
            <BarChart3 className="w-4 h-4 mr-2" />
            Generate Executive Report
          </Button>
          <Button>
            Export Dashboard
          </Button>
        </div>
      </div>

      {/* Executive Summary */}
      <Card className="border-2 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Executive Summary
          </CardTitle>
          <CardDescription>
            High-level security posture overview for executive reporting
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Overall Risk Level</p>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                  MEDIUM
                </Badge>
                <span className="text-2xl font-bold">7.2/10</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Compliance Posture</p>
              <div className="flex items-center gap-2">
                <Progress value={78} className="flex-1" />
                <span className="text-2xl font-bold">78%</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Active Threats</p>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-500" />
                <span className="text-2xl font-bold text-red-600">5</span>
                <span className="text-sm text-muted-foreground">High Priority</span>
              </div>
            </div>
          </div>
          
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <p className="text-sm leading-relaxed">
              <strong>Executive Summary:</strong> The organization maintains a moderate risk posture with 78% compliance 
              across implemented frameworks. Five high-priority risks require immediate executive attention, primarily 
              related to third-party vendor assessments and cloud infrastructure security. Investment in automated 
              security controls and threat detection capabilities is recommended for Q2.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Strategic Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Security Investment ROI</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">245%</div>
            <p className="text-xs text-muted-foreground">Risk reduction vs. investment</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Time to Remediation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12.5 days</div>
            <p className="text-xs text-muted-foreground">Average critical risk resolution</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Audit Readiness</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">92%</div>
            <p className="text-xs text-muted-foreground">Controls with evidence</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Threat Exposure</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">Medium</div>
            <p className="text-xs text-muted-foreground">External attack surface</p>
          </CardContent>
        </Card>
      </div>

      {/* Risk Trend and Compliance Matrix */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Risk Posture Trend</CardTitle>
            <CardDescription>6-month risk level progression</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <BarChart3 className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">Risk Trend Visualization</p>
                <p className="text-sm">Interactive chart showing risk reduction over time</p>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Jan 2025:</span>
                    <Badge variant="destructive">High</Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Current:</span>
                    <Badge variant="secondary">Medium</Badge>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Compliance Framework Maturity</CardTitle>
            <CardDescription>Implementation status across frameworks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">NIST Cybersecurity Framework</span>
                <span className="text-muted-foreground">82%</span>
              </div>
              <Progress value={82} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">CIS Controls v8.0</span>
                <span className="text-muted-foreground">74%</span>
              </div>
              <Progress value={74} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">ISO 27001:2022</span>
                <span className="text-muted-foreground">68%</span>
              </div>
              <Progress value={68} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">SOC 2 Type II</span>
                <span className="text-muted-foreground">91%</span>
              </div>
              <Progress value={91} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Strategic Risks */}
      <Card>
        <CardHeader>
          <CardTitle>Strategic Risk Portfolio</CardTitle>
          <CardDescription>Top business-impacting risks requiring executive attention</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex-1">
                <h4 className="font-semibold">Third-Party Vendor Risk</h4>
                <p className="text-sm text-muted-foreground">Inadequate security assessments of critical suppliers</p>
              </div>
              <div className="flex items-center gap-4">
                <Badge variant="destructive">Critical</Badge>
                <div className="text-right">
                  <p className="text-sm font-medium">$2.1M</p>
                  <p className="text-xs text-muted-foreground">Potential Impact</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex-1">
                <h4 className="font-semibold">Cloud Infrastructure Exposure</h4>
                <p className="text-sm text-muted-foreground">Misconfigured cloud services with public access</p>
              </div>
              <div className="flex items-center gap-4">
                <Badge variant="destructive">High</Badge>
                <div className="text-right">
                  <p className="text-sm font-medium">$850K</p>
                  <p className="text-xs text-muted-foreground">Potential Impact</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex-1">
                <h4 className="font-semibold">Data Privacy Compliance Gap</h4>
                <p className="text-sm text-muted-foreground">GDPR/CCPA compliance requirements not fully implemented</p>
              </div>
              <div className="flex items-center gap-4">
                <Badge className="bg-orange-100 text-orange-800">High</Badge>
                <div className="text-right">
                  <p className="text-sm font-medium">$1.2M</p>
                  <p className="text-xs text-muted-foreground">Potential Impact</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}