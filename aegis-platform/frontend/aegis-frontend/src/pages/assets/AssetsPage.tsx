import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Database, Download, Upload, Eye, Edit, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { assetsApi } from '@/lib/api';
import { DataTable, CriticalityBadge, StatusBadge } from '@/components/ui/data-table';
import { ColumnDef } from '@tanstack/react-table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { AddAssetDialog } from '@/components/dialogs/AddAssetDialog';
import { EditAssetDialog } from '@/components/dialogs/EditAssetDialog';
import { ImportAssetsDialog } from '@/components/dialogs/ImportAssetsDialog';

// Asset interface for type safety
interface Asset {
  id: number;
  name: string;
  description?: string;
  asset_type: string;
  criticality: string;
  status: string;
  environment?: string;
  owner_id?: number;
  ip_address?: string;
  hostname?: string;
  operating_system?: string;
  location?: string;
  business_unit?: string;
  created_at?: string;
  updated_at?: string;
}

export default function AssetsPage() {
  const navigate = useNavigate();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        setLoading(true);
        const response = await assetsApi.getAll();
        setAssets(response.items || []);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch assets');
        console.error('Error fetching assets:', err);
        // Use empty array if API fails
        setAssets([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAssets();
  }, []);

  // Define columns for the data table
  const columns = useMemo<ColumnDef<Asset>[]>(
    () => [
      {
        accessorKey: 'name',
        header: 'Asset Name',
        cell: ({ row }) => {
          const asset = row.original;
          return (
            <div className="flex flex-col">
              <span className="font-medium">{asset.name}</span>
              {asset.description && (
                <span className="text-sm text-muted-foreground truncate max-w-[200px]">
                  {asset.description}
                </span>
              )}
            </div>
          );
        },
      },
      {
        accessorKey: 'asset_type',
        header: 'Type',
        cell: ({ getValue }) => (
          <Badge variant="outline" className="capitalize">
            {(getValue() as string) || 'Unknown'}
          </Badge>
        ),
      },
      {
        accessorKey: 'criticality',
        header: 'Criticality',
        cell: ({ getValue }) => (
          <CriticalityBadge level={getValue() as string} />
        ),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ getValue }) => {
          const status = getValue() as string;
          const getVariant = () => {
            switch (status?.toLowerCase()) {
              case 'active': return 'default';
              case 'inactive': return 'secondary';
              case 'maintenance': return 'outline';
              default: return 'secondary';
            }
          };
          return <StatusBadge status={status} variant={getVariant()} />;
        },
      },
      {
        accessorKey: 'environment',
        header: 'Environment',
        cell: ({ getValue }) => {
          const env = getValue() as string;
          return (
            <span className="capitalize text-sm">
              {env || 'Unknown'}
            </span>
          );
        },
      },
      {
        accessorKey: 'ip_address',
        header: 'IP Address',
        cell: ({ getValue }) => {
          const ip = getValue() as string;
          return (
            <code className="text-xs bg-muted px-1 py-0.5 rounded">
              {ip || 'N/A'}
            </code>
          );
        },
      },
      {
        accessorKey: 'updated_at',
        header: 'Last Updated',
        cell: ({ getValue }) => {
          const date = getValue() as string;
          return date ? (
            <span className="text-sm text-muted-foreground">
              {new Date(date).toLocaleDateString()}
            </span>
          ) : (
            <span className="text-sm text-muted-foreground">Never</span>
          );
        },
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => {
          const asset = row.original;
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
                <DropdownMenuItem onClick={() => handleViewAsset(asset.id)}>
                  <Eye className="mr-2 h-4 w-4" />
                  View Details
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleEditAsset(asset.id)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit Asset
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          );
        },
      },
    ],
    []
  );

  const handleAddAsset = () => {
    console.log('Add Asset clicked - Opening asset creation dialog');
    setShowAddDialog(true);
  };

  const handleAssetAdded = () => {
    console.log('Asset added successfully - refreshing asset list');
    // Refresh the asset list
    const fetchAssets = async () => {
      try {
        setLoading(true);
        const response = await assetsApi.getAll();
        setAssets(response.items || []);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch assets');
        console.error('Error fetching assets:', err);
        setAssets([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAssets();
  };

  const handleImport = () => {
    console.log('Import clicked - Opening import dialog');
    setShowImportDialog(true);
  };

  const handleExport = () => {
    console.log('Export clicked - Generating CSV export');
    
    // Generate CSV from current assets data
    const csvHeaders = 'Name,Description,Type,Criticality,Status,Environment,Owner,IP Address,Hostname,Location\n';
    const csvContent = assets.map(asset => 
      `"${asset.name || ''}","${asset.description || ''}","${asset.asset_type || ''}","${asset.criticality || ''}","${asset.status || ''}","${asset.environment || ''}","${asset.owner_id || ''}","${asset.ip_address || ''}","${asset.hostname || ''}","${asset.location || ''}"`
    ).join('\n');
    
    const csvData = csvHeaders + csvContent;
    const blob = new Blob([csvData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `assets_export_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    console.log(`✅ Exported ${assets.length} assets to CSV`);
  };

  const handleViewAsset = (assetId: number) => {
    console.log('View Asset clicked for asset:', assetId);
    navigate(`/assets/${assetId}`);
  };

  const handleEditAsset = (assetId: number) => {
    console.log('Edit Asset clicked for asset:', assetId);
    const asset = assets.find(a => a.id === assetId);
    if (asset) {
      setSelectedAsset(asset);
      setShowEditDialog(true);
    }
  };

  const handleAssetsImported = () => {
    console.log('Assets imported - Refreshing list');
    // Refresh the assets list
    const fetchAssets = async () => {
      try {
        setLoading(true);
        const response = await assetsApi.getAll();
        setAssets(response.items || []);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch assets');
        console.error('Error fetching assets:', err);
        setAssets([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAssets();
  };

  const handleAssetUpdated = () => {
    console.log('Asset updated successfully - refreshing asset list');
    const fetchAssets = async () => {
      try {
        setLoading(true);
        const response = await assetsApi.getAll();
        setAssets(response.items || []);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch assets');
        console.error('Error fetching assets:', err);
        setAssets([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAssets();
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
            Manage and track your organization's critical assets
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleImport}>
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleAddAsset}>
            <Plus className="h-4 w-4 mr-2" />
            Add Asset
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">Error: {error}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Showing example data while backend is unavailable.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{assets.length}</div>
            <p className="text-xs text-muted-foreground">
              Assets in system
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical Assets</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assets.filter(a => a.criticality === 'critical').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Require immediate attention
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Assets</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assets.filter(a => a.status === 'active').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently operational
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Asset Types</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(assets.map(a => a.asset_type)).size}
            </div>
            <p className="text-xs text-muted-foreground">
              Different asset categories
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Assets ({assets.length})</CardTitle>
          <CardDescription>
            A comprehensive view of all organizational assets with advanced filtering and search
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={columns}
            data={assets}
            loading={loading}
            searchPlaceholder="Search assets by name, type, or description..."
            emptyStateTitle="No assets found"
            emptyStateDescription="Get started by adding your first asset to track your organization's resources"
            emptyStateAction={
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add First Asset
              </Button>
            }
            showSearch={true}
            showColumnToggle={true}
            showPagination={true}
            pageSize={10}
            onRowClick={(asset) => {
              console.log('View asset:', asset);
              navigate(`/assets/${asset.id}`);
            }}
          />
        </CardContent>
      </Card>

      {/* Add Asset Dialog */}
      <AddAssetDialog
        open={showAddDialog}
        onOpenChange={setShowAddDialog}
        onAssetAdded={handleAssetAdded}
      />

      {/* Edit Asset Dialog */}
      <EditAssetDialog
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
        asset={selectedAsset}
        onAssetUpdated={handleAssetUpdated}
      />

      {/* Import Assets Dialog */}
      <ImportAssetsDialog
        open={showImportDialog}
        onOpenChange={setShowImportDialog}
        onAssetsImported={handleAssetsImported}
      />
    </div>
  );
}