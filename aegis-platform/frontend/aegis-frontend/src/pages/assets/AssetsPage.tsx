import { useState } from 'react';
import { Plus, Database, Filter, Download, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

export default function AssetsPage() {
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data - in real app this would come from API
  const assets = [
    {
      id: 1,
      name: 'Web Server 01',
      type: 'Server',
      criticality: 'critical',
      status: 'active',
      owner: 'IT Team',
      lastUpdated: '2025-07-08'
    },
    {
      id: 2,
      name: 'Database Server - Production',
      type: 'Database',
      criticality: 'critical',
      status: 'active',
      owner: 'DevOps Team',
      lastUpdated: '2025-07-07'
    },
    {
      id: 3,
      name: 'Employee Workstation Fleet',
      type: 'Workstation',
      criticality: 'medium',
      status: 'active',
      owner: 'HR Department',
      lastUpdated: '2025-07-06'
    },
    {
      id: 4,
      name: 'Network Firewall',
      type: 'Network Equipment',
      criticality: 'high',
      status: 'active',
      owner: 'Security Team',
      lastUpdated: '2025-07-08'
    }
  ];

  const getCriticalityColor = (criticality: string) => {
    switch (criticality) {
      case 'critical': return 'destructive';
      case 'high': return 'secondary';
      case 'medium': return 'outline';
      case 'low': return 'secondary';
      default: return 'secondary';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Database className="h-8 w-8" />
            Asset Management
          </h1>
          <p className="text-muted-foreground">
            Manage and track your organization's assets
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline">
            <Upload className="w-4 h-4 mr-2" />
            Import CSV
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Asset
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search assets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline">
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Assets List */}
      <Card>
        <CardHeader>
          <CardTitle>Assets ({assets.length})</CardTitle>
          <CardDescription>
            Complete inventory of organizational assets
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {assets.map((asset) => (
              <div key={asset.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold">{asset.name}</h3>
                    <Badge variant={getCriticalityColor(asset.criticality)}>
                      {asset.criticality}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                    <span>Type: {asset.type}</span>
                    <span>Owner: {asset.owner}</span>
                    <span>Updated: {asset.lastUpdated}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    {asset.status}
                  </Badge>
                  <Button variant="ghost" size="sm">
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