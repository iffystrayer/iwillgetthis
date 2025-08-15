import { useState, useEffect, useMemo } from 'react';
import { Users, Plus, Edit, UserCheck, UserX, Eye, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { usersApi } from '@/lib/api';
import { DataTable, StatusBadge } from '@/components/ui/data-table';
import { createCommonBulkActions } from '@/components/ui/bulk-actions-toolbar';
import { BulkOperationProgress, useBulkOperationProgress } from '@/components/ui/bulk-operation-progress';
import { ColumnDef } from '@tanstack/react-table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { AddUserDialog } from '@/components/dialogs/AddUserDialog';
import { EditUserDialog } from '@/components/dialogs/EditUserDialog';
import { InviteUsersDialog } from '@/components/dialogs/InviteUsersDialog';

// User interface for type safety
interface User {
  id: number;
  full_name: string;
  email: string;
  role: string;
  status: string;
  last_login?: string;
  created_at?: string;
  updated_at?: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState<User[]>([]);

  // Bulk operation progress tracking
  const {
    isOpen: isBulkProgressOpen,
    operation: currentOperation,
    items: progressItems,
    canCancel: canCancelOperation,
    startOperation,
    updateItemStatus,
    closeProgress,
  } = useBulkOperationProgress();

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await usersApi.getAll();
      setUsers(response.items || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch users');
      console.error('Error fetching users:', err);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Define columns for the data table
  const columns = useMemo<ColumnDef<User>[]>(
    () => [
      {
        accessorKey: 'full_name',
        header: 'User',
        cell: ({ row }) => {
          const user = row.original;
          return (
            <div className="flex flex-col">
              <span className="font-medium">{user.full_name}</span>
              <span className="text-sm text-muted-foreground">
                {user.email}
              </span>
            </div>
          );
        },
      },
      {
        accessorKey: 'role',
        header: 'Role',
        cell: ({ getValue }) => {
          const role = getValue() as string;
          const getVariant = () => {
            switch (role?.toLowerCase()) {
              case 'admin': return 'destructive';
              case 'security analyst': return 'secondary';
              case 'risk manager': return 'outline';
              case 'compliance officer': return 'default';
              default: return 'secondary';
            }
          };
          return <Badge variant={getVariant()} className="capitalize">
            {role || 'No Role'}
          </Badge>;
        },
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
              case 'suspended': return 'destructive';
              default: return 'secondary';
            }
          };
          return <StatusBadge status={status} variant={getVariant()} />;
        },
      },
      {
        accessorKey: 'last_login',
        header: 'Last Login',
        cell: ({ getValue }) => {
          const date = getValue() as string;
          if (!date) return <span className="text-sm text-muted-foreground">Never</span>;
          return (
            <span className="text-sm text-muted-foreground">
              {new Date(date).toLocaleString()}
            </span>
          );
        },
      },
      {
        accessorKey: 'created_at',
        header: 'Created',
        cell: ({ getValue }) => {
          const date = getValue() as string;
          return date ? (
            <span className="text-sm text-muted-foreground">
              {new Date(date).toLocaleDateString()}
            </span>
          ) : (
            <span className="text-sm text-muted-foreground">N/A</span>
          );
        },
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => {
          const user = row.original;
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
                <DropdownMenuItem onClick={() => handleViewDetails(user.id)}>
                  <Eye className="mr-2 h-4 w-4" />
                  View Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleEditUser(user.id)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit User
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          );
        },
      },
    ],
    []
  );



  const handleAddUser = () => {
    console.log('Add User clicked - Opening dialog');
    setShowAddDialog(true);
  };

  const handleInviteUsers = () => {
    console.log('Invite Users clicked - Opening invite dialog');
    setShowInviteDialog(true);
  };

  const handleUsersInvited = () => {
    console.log('Users invited successfully - refreshing user list');
    fetchUsers();
  };

  const handleViewDetails = (userId: number) => {
    console.log('View Details clicked for user:', userId);
    // TODO: Navigate to user details page
  };

  const handleEditUser = (userId: number) => {
    console.log('Edit User clicked for user:', userId);
    const user = users.find(u => u.id === userId);
    if (user) {
      setSelectedUser(user);
      setShowEditDialog(true);
    }
  };

  const handleUserUpdated = () => {
    console.log('User updated successfully - refreshing user list');
    fetchUsers();
  };

  const handleUserAdded = () => {
    console.log('User added successfully - refreshing user list');
    // Refresh the user list
    fetchUsers();
  };

  // Bulk operations handlers with progress tracking
  const handleBulkDelete = async () => {
    console.log('Bulk delete users:', selectedUsers.map(u => u.id));
    
    // Start progress tracking
    startOperation(
      `Deleting ${selectedUsers.length} Users`,
      selectedUsers.map(user => ({ id: user.id, name: user.full_name })),
      true // Can be cancelled
    );

    // Simulate bulk deletion with progress updates
    for (const user of selectedUsers) {
      try {
        updateItemStatus(user.id, 'processing');
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // TODO: Replace with actual API call
        // await usersApi.delete(user.id);
        
        updateItemStatus(user.id, 'completed');
      } catch (error) {
        updateItemStatus(user.id, 'failed', error instanceof Error ? error.message : 'Delete failed');
      }
    }
    
    // Refresh user list after completion
    fetchUsers();
  };

  const handleBulkUpdateStatus = async () => {
    console.log('Bulk update status for users:', selectedUsers.map(u => u.id));
    
    // Start progress tracking
    startOperation(
      `Updating Status for ${selectedUsers.length} Users`,
      selectedUsers.map(user => ({ id: user.id, name: user.full_name })),
      true
    );

    // Simulate bulk status update with progress
    for (const user of selectedUsers) {
      try {
        updateItemStatus(user.id, 'processing');
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 600));
        
        // TODO: Replace with actual API call
        // await usersApi.updateStatus(user.id, newStatus);
        
        updateItemStatus(user.id, 'completed');
      } catch (error) {
        updateItemStatus(user.id, 'failed', error instanceof Error ? error.message : 'Status update failed');
      }
    }
    
    // Refresh user list after completion
    fetchUsers();
  };

  const handleBulkUpdateRole = async () => {
    console.log('Bulk update role for users:', selectedUsers.map(u => u.id));
    
    // Start progress tracking
    startOperation(
      `Updating Roles for ${selectedUsers.length} Users`,
      selectedUsers.map(user => ({ id: user.id, name: user.full_name })),
      true
    );

    // Simulate bulk role update with progress
    for (const user of selectedUsers) {
      try {
        updateItemStatus(user.id, 'processing');
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 700));
        
        // TODO: Replace with actual API call
        // await usersApi.updateRole(user.id, newRole);
        
        updateItemStatus(user.id, 'completed');
      } catch (error) {
        updateItemStatus(user.id, 'failed', error instanceof Error ? error.message : 'Role update failed');
      }
    }
    
    // Refresh user list after completion
    fetchUsers();
  };

  const handleBulkExport = async () => {
    console.log('Bulk export selected users:', selectedUsers.map(u => u.id));
    
    // Start progress tracking for export
    startOperation(
      `Exporting ${selectedUsers.length} Users`,
      selectedUsers.map(user => ({ id: user.id, name: user.full_name })),
      false // Export cannot be cancelled
    );

    try {
      // Process each user for export with progress updates
      for (const user of selectedUsers) {
        updateItemStatus(user.id, 'processing');
        
        // Simulate processing time for each user
        await new Promise(resolve => setTimeout(resolve, 200));
        
        updateItemStatus(user.id, 'completed');
      }

      // Generate CSV from selected users
      const csvHeaders = 'Full Name,Email,Role,Status,Last Login,Created\n';
      const csvContent = selectedUsers.map(user => 
        `"${user.full_name || ''}","${user.email || ''}","${user.role || ''}","${user.status || ''}","${user.last_login || ''}","${user.created_at || ''}"`
      ).join('\n');
      
      const csvData = csvHeaders + csvContent;
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `selected_users_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      console.log(`✅ Exported ${selectedUsers.length} selected users to CSV`);
    } catch (error) {
      // Mark all remaining users as failed if export fails
      selectedUsers.forEach(user => {
        updateItemStatus(user.id, 'failed', 'Export failed');
      });
    }
  };

  // Create bulk actions for users (custom actions for user management)
  const bulkActions = useMemo(() => {
    return [
      {
        id: 'export',
        label: 'Export Selected',
        icon: Users,
        variant: 'secondary' as const,
        onClick: handleBulkExport,
      },
      {
        id: 'updateRole',
        label: 'Update Role',
        icon: UserCheck,
        variant: 'secondary' as const,
        onClick: handleBulkUpdateRole,
      },
      {
        id: 'updateStatus',
        label: 'Update Status',
        icon: UserX,
        variant: 'secondary' as const,
        onClick: handleBulkUpdateStatus,
      },
      {
        id: 'delete',
        label: 'Delete Users',
        icon: UserX,
        variant: 'destructive' as const,
        onClick: handleBulkDelete,
      },
    ];
  }, [selectedUsers]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Users className="h-8 w-8" />
            User Management
          </h1>
          <p className="text-muted-foreground">
            Manage user accounts, roles, and permissions
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleInviteUsers}>
            <UserCheck className="h-4 w-4 mr-2" />
            Invite Users
          </Button>
          <Button onClick={handleAddUser}>
            <Plus className="h-4 w-4 mr-2" />
            Add User
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
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{users.length}</div>
            <p className="text-xs text-muted-foreground">
              Registered users
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {users.filter(u => u.status?.toLowerCase() === 'active').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently active
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inactive Users</CardTitle>
            <UserX className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {users.filter(u => u.status?.toLowerCase() !== 'active').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Need attention
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Roles</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(users.map(u => u.role)).size}
            </div>
            <p className="text-xs text-muted-foreground">
              Different roles
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Users ({users.length})</CardTitle>
          <CardDescription>
            Comprehensive view of all user accounts with advanced filtering and search
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={columns}
            data={users}
            loading={loading}
            searchPlaceholder="Search users by name, email, or role..."
            emptyStateTitle="No users found"
            emptyStateDescription="Get started by adding your first user to the system"
            emptyStateAction={
              <Button onClick={handleAddUser}>
                <Plus className="h-4 w-4 mr-2" />
                Add First User
              </Button>
            }
            showSearch={true}
            showColumnToggle={true}
            showPagination={true}
            pageSize={10}
            onRowClick={(user) => {
              handleViewDetails(user.id);
            }}
            rowClassName={(user) => {
              // Highlight inactive or suspended users
              const isInactive = user.status?.toLowerCase() === 'inactive';
              const isSuspended = user.status?.toLowerCase() === 'suspended';
              if (isSuspended) return 'bg-red-50 hover:bg-red-100';
              if (isInactive) return 'bg-gray-50 hover:bg-gray-100';
              return '';
            }}
            enableBulkSelect={true}
            bulkActions={bulkActions}
            onBulkSelectionChange={setSelectedUsers}
            getRowId={(row) => row.id.toString()}
          />
        </CardContent>
      </Card>

      {/* Add User Dialog */}
      <AddUserDialog
        open={showAddDialog}
        onOpenChange={setShowAddDialog}
        onUserAdded={handleUserAdded}
      />

      {/* Edit User Dialog */}
      <EditUserDialog
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
        user={selectedUser}
        onUserUpdated={handleUserUpdated}
      />

      {/* Invite Users Dialog */}
      <InviteUsersDialog
        open={showInviteDialog}
        onOpenChange={setShowInviteDialog}
        onUsersInvited={handleUsersInvited}
      />

      {/* Bulk Operation Progress Dialog */}
      <BulkOperationProgress
        isOpen={isBulkProgressOpen}
        onClose={closeProgress}
        operation={currentOperation}
        items={progressItems}
        canCancel={canCancelOperation}
        showDetails={true}
      />
    </div>
  );
}