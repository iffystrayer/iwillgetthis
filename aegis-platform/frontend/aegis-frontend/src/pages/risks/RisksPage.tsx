import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, AlertTriangle, TrendingUp, Eye, Edit, MoreHorizontal, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { DataTable, CriticalityBadge, StatusBadge } from '@/components/ui/data-table';
import { createCommonBulkActions } from '@/components/ui/bulk-actions-toolbar';
import { ColumnDef } from '@tanstack/react-table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { AddRiskDialog } from '@/components/dialogs/AddRiskDialog';
import { EditRiskDialog } from '@/components/dialogs/EditRiskDialog';

// Risk interface for type safety
interface Risk {
  id: number;
  title: string;
  category: string;
  level: string;
  score: number;
  status: string;
  owner: string;
  dueDate: string;
}

export default function RisksPage() {
  const navigate = useNavigate();
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null);
  const [selectedRisks, setSelectedRisks] = useState<Risk[]>([]);

  // Mock data with more comprehensive examples
  const risks: Risk[] = [
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

  // Define columns for the data table
  const columns = useMemo<ColumnDef<Risk>[]>(
    () => [
      {
        accessorKey: 'title',
        header: 'Risk Title',
        cell: ({ row }) => {
          const risk = row.original;
          return (
            <div className="flex flex-col max-w-[300px]">
              <span className="font-medium">{risk.title}</span>
              <span className="text-sm text-muted-foreground">
                ID: {risk.id} • {risk.category}
              </span>
            </div>
          );
        },
      },
      {
        accessorKey: 'level',
        header: 'Risk Level',
        cell: ({ getValue }) => (
          <CriticalityBadge level={getValue() as string} />
        ),
      },
      {
        accessorKey: 'score',
        header: 'Risk Score',
        cell: ({ getValue }) => {
          const score = getValue() as number;
          const getScoreColor = () => {
            if (score >= 8) return 'text-red-600';
            if (score >= 6) return 'text-orange-600';
            if (score >= 4) return 'text-yellow-600';
            return 'text-green-600';
          };
          return (
            <div className="flex items-center gap-2">
              <span className={`font-mono text-sm font-semibold ${getScoreColor()}`}>
                {score.toFixed(1)}
              </span>
              <Progress value={score * 10} className="w-16 h-2" />
            </div>
          );
        },
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ getValue }) => {
          const status = getValue() as string;
          const getVariant = () => {
            switch (status?.toLowerCase()) {
              case 'mitigating': return 'default';
              case 'assessed': return 'secondary';
              case 'identified': return 'destructive';
              case 'monitoring': return 'outline';
              default: return 'secondary';
            }
          };
          return <StatusBadge status={status} variant={getVariant()} />;
        },
      },
      {
        accessorKey: 'owner',
        header: 'Owner',
        cell: ({ getValue }) => (
          <span className="text-sm">{getValue() as string}</span>
        ),
      },
      {
        accessorKey: 'dueDate',
        header: 'Due Date',
        cell: ({ getValue }) => {
          const date = new Date(getValue() as string);
          const isOverdue = date < new Date();
          return (
            <span className={`text-sm ${isOverdue ? 'text-red-600 font-semibold' : 'text-muted-foreground'}`}>
              {date.toLocaleDateString()}
            </span>
          );
        },
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => {
          const risk = row.original;
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <span className="sr-only">Open menu</span>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => handleViewDetails(risk.id)}>
                  <Eye className="mr-2 h-4 w-4" />
                  View Details
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleEditRisk(risk.id)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit Risk
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          );
        },
      },
    ],
    []
  );

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
    setShowAddDialog(true);
  };

  const handleRiskAdded = () => {
    console.log('Risk added successfully - refreshing risk list');
    // TODO: Refresh the risk list from API
  };

  const handleRiskMatrix = () => {
    console.log('Risk Matrix clicked - Opening risk matrix view');
    alert('Risk Matrix visualization - Would show probability vs impact matrix');
  };

  const handleFilters = () => {
    console.log('Filters clicked - Opening filter options');
    alert('Risk filters - Would show advanced filtering options');
  };


  const handleViewDetails = (riskId: number) => {
    console.log('View Details clicked for risk:', riskId);
    navigate(`/risks/${riskId}`);
  };

  const handleEditRisk = (riskId: number) => {
    console.log('Edit Risk clicked for risk:', riskId);
    const risk = risks.find(r => r.id === riskId);
    if (risk) {
      setSelectedRisk(risk);
      setShowEditDialog(true);
    }
  };

  const handleRiskUpdated = () => {
    console.log('Risk updated successfully - refreshing risk list');
    // TODO: Refresh the risk list from API
  };

  // Bulk operations handlers
  const handleBulkDelete = async () => {
    console.log('Bulk delete risks:', selectedRisks.map(r => r.id));
    // TODO: Implement bulk delete API call
    alert(`Would delete ${selectedRisks.length} risks`);
  };

  const handleBulkUpdateStatus = async () => {
    console.log('Bulk update status for risks:', selectedRisks.map(r => r.id));
    // TODO: Implement bulk status update dialog
    alert(`Would update status for ${selectedRisks.length} risks`);
  };

  const handleBulkAssign = async () => {
    console.log('Bulk assign risks:', selectedRisks.map(r => r.id));
    // TODO: Implement bulk assignment dialog
    alert(`Would assign ${selectedRisks.length} risks`);
  };

  const handleBulkExport = () => {
    console.log('Bulk export selected risks:', selectedRisks.map(r => r.id));
    
    // Generate CSV from selected risks
    const csvHeaders = 'Title,Category,Level,Score,Status,Owner,Due Date\n';
    const csvContent = selectedRisks.map(risk => 
      `"${risk.title || ''}","${risk.category || ''}","${risk.level || ''}","${risk.score || ''}","${risk.status || ''}","${risk.owner || ''}","${risk.dueDate || ''}"`
    ).join('\n');
    
    const csvData = csvHeaders + csvContent;
    const blob = new Blob([csvData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `selected_risks_export_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    console.log(`✅ Exported ${selectedRisks.length} selected risks to CSV`);
  };

  // Create bulk actions for risks
  const bulkActions = useMemo(() => {
    return createCommonBulkActions(selectedRisks, {
      onExport: handleBulkExport,
      onUpdateStatus: handleBulkUpdateStatus,
      onAssign: handleBulkAssign,
      onDelete: handleBulkDelete,
    });
  }, [selectedRisks]);

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
          <Button variant="outline" onClick={handleFilters}>
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
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


      {/* Enhanced Risk Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Risk Register ({risks.length})</CardTitle>
          <CardDescription>
            Comprehensive view of organizational risk portfolio with advanced filtering and analytics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={columns}
            data={risks}
            loading={false}
            searchPlaceholder="Search risks by title, category, or owner..."
            emptyStateTitle="No risks found"
            emptyStateDescription="Start building your risk register by adding your first organizational risk"
            emptyStateAction={
              <Button onClick={handleAddRisk}>
                <Plus className="h-4 w-4 mr-2" />
                Add First Risk
              </Button>
            }
            showSearch={true}
            showColumnToggle={true}
            showPagination={true}
            pageSize={10}
            onRowClick={(risk) => {
              handleViewDetails(risk.id);
            }}
            rowClassName={(risk) => {
              // Highlight overdue or critical risks
              const isOverdue = new Date(risk.dueDate) < new Date();
              const isCritical = risk.level === 'critical';
              if (isOverdue && isCritical) return 'bg-red-50 hover:bg-red-100';
              if (isOverdue) return 'bg-orange-50 hover:bg-orange-100';
              if (isCritical) return 'bg-yellow-50 hover:bg-yellow-100';
              return '';
            }}
            enableBulkSelect={true}
            bulkActions={bulkActions}
            onBulkSelectionChange={setSelectedRisks}
            getRowId={(row) => row.id.toString()}
          />
        </CardContent>
      </Card>

      {/* Add Risk Dialog */}
      <AddRiskDialog
        open={showAddDialog}
        onOpenChange={setShowAddDialog}
        onRiskAdded={handleRiskAdded}
      />

      {/* Edit Risk Dialog */}
      <EditRiskDialog
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
        risk={selectedRisk}
        onRiskUpdated={handleRiskUpdated}
      />
    </div>
  );
}