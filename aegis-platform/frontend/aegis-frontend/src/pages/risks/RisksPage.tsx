import { useState } from 'react';
import { Plus, AlertTriangle, Filter, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

export default function RisksPage() {
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data
  const risks = [
    {
      id: 1,
      title: 'Unpatched Web Server Vulnerability',
      category: 'Technical',
      level: 'critical',
      score: 9.2,
      status: 'mitigating',
      owner: 'Security Team',
      dueDate: '2025-07-15'
    },
    {
      id: 2,
      title: 'Third-Party Vendor Data Access',
      category: 'Operational',
      level: 'high',
      score: 7.8,
      status: 'assessed',
      owner: 'Procurement',
      dueDate: '2025-07-20'
    },
    {
      id: 3,
      title: 'Inadequate Backup Recovery Testing',
      category: 'Technical',
      level: 'medium',
      score: 5.5,
      status: 'identified',
      owner: 'IT Operations',
      dueDate: '2025-07-25'
    },
    {
      id: 4,
      title: 'Employee Security Awareness Gap',
      category: 'Human Factor',
      level: 'medium',
      score: 6.1,
      status: 'monitoring',
      owner: 'HR Department',
      dueDate: '2025-08-01'
    }
  ];

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'destructive';
      case 'high': return 'secondary';
      case 'medium': return 'outline';
      case 'low': return 'secondary';
      default: return 'secondary';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'mitigating': return 'text-blue-600';
      case 'assessed': return 'text-orange-600';
      case 'identified': return 'text-red-600';
      case 'monitoring': return 'text-green-600';
      default: return 'text-muted-foreground';
    }
  };

  const handleAddRisk = () => {
    console.log('Add Risk clicked - Opening risk creation dialog');
    alert('Add Risk functionality would open a dialog to create new risks');
    // TODO: Implement add risk dialog
  };

  const handleRiskMatrix = () => {
    console.log('Risk Matrix clicked - Opening risk matrix view');
    alert('Risk Matrix functionality would show risks plotted on probability vs impact matrix');
    // TODO: Implement risk matrix visualization
  };

  const handleFilters = () => {
    console.log('Filters clicked - Opening filters dialog');
    alert('Filters functionality would open a filters panel for risks');
    // TODO: Implement filters dialog
  };

  const handleViewDetails = (riskId: number) => {
    console.log('View Details clicked for risk:', riskId);
    alert(`View Details functionality would navigate to detailed view for risk ${riskId}`);
    // TODO: Navigate to risk details page
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <AlertTriangle className="h-8 w-8" />
            Risk Register
          </h1>
          <p className="text-muted-foreground">
            Monitor and manage organizational risks
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRiskMatrix}>
            <TrendingUp className="w-4 h-4 mr-2" />
            Risk Matrix
          </Button>
          <Button onClick={handleAddRisk}>
            <Plus className="w-4 h-4 mr-2" />
            Add Risk
          </Button>
        </div>
      </div>

      {/* Risk Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Risks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{risks.length}</div>
            <p className="text-xs text-muted-foreground">Active risks tracked</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Critical/High</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">2</div>
            <p className="text-xs text-muted-foreground">Require immediate attention</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Mitigation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">1</div>
            <p className="text-xs text-muted-foreground">Active remediation</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Average Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">7.2</div>
            <p className="text-xs text-muted-foreground">Out of 10</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search risks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline" onClick={handleFilters}>
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Risks List */}
      <Card>
        <CardHeader>
          <CardTitle>Risk Register</CardTitle>
          <CardDescription>
            Current organizational risk portfolio
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {risks.map((risk) => (
              <div key={risk.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold">{risk.title}</h3>
                    <Badge variant={getRiskLevelColor(risk.level)}>
                      {risk.level}
                    </Badge>
                    <div className="text-sm font-medium">
                      Score: {risk.score}/10
                    </div>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                    <span>Category: {risk.category}</span>
                    <span>Owner: {risk.owner}</span>
                    <span>Due: {risk.dueDate}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-medium ${getStatusColor(risk.status)}`}>
                    {risk.status.charAt(0).toUpperCase() + risk.status.slice(1)}
                  </span>
                  <Button variant="ghost" size="sm" onClick={() => handleViewDetails(risk.id)}>
                    View Details
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}