import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Download, Search, RefreshCw, Shield, AlertTriangle, Eye } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { DataTable } from '@/components/ui/data-table';
import { api } from '@/lib/api';
import { useNotifications } from '@/hooks/useNotifications';

interface AuditEvent {
  id: number;
  event_type: string;
  entity_type: string;
  entity_id?: number;
  user_id?: number;
  action: string;
  description: string;
  source: string;
  ip_address?: string;
  user_agent?: string;
  risk_level: string;
  timestamp: string;
}

interface AuditTrailResponse {
  total_count: number;
  results: AuditEvent[];
  limit: number;
  offset: number;
  has_more: boolean;
  filters_applied?: Record<string, any>;
}

interface SecurityEventSummary {
  period_days: number;
  total_security_events: number;
  events_by_type: Record<string, number>;
  events_by_user: Record<number, number>;
  suspicious_ip_addresses: Record<string, number>;
  recent_events: Array<{
    id: number;
    event_type: string;
    action: string;
    description: string;
    entity_type: string;
    user_id?: number;
    ip_address?: string;
    risk_level: string;
    timestamp: string;
  }>;
  summary: {
    high_risk_events: number;
    failed_login_attempts: number;
    unauthorized_access_attempts: number;
    config_changes: number;
  };
}

const getRiskLevelColor = (riskLevel: string) => {
  switch (riskLevel.toLowerCase()) {
    case 'critical':
      return 'bg-red-500 text-white';
    case 'high':
      return 'bg-orange-500 text-white';
    case 'medium':
      return 'bg-yellow-500 text-black';
    case 'low':
      return 'bg-green-500 text-white';
    default:
      return 'bg-gray-500 text-white';
  }
};

const getRiskLevelIcon = (riskLevel: string) => {
  switch (riskLevel.toLowerCase()) {
    case 'critical':
    case 'high':
      return <AlertTriangle className="h-4 w-4" />;
    case 'medium':
      return <Shield className="h-4 w-4" />;
    case 'low':
      return <Eye className="h-4 w-4" />;
    default:
      return <Eye className="h-4 w-4" />;
  }
};

export default function AuditTrailPage() {
  const [auditData, setAuditData] = useState<AuditTrailResponse | null>(null);
  const [securityEvents, setSecurityEvents] = useState<SecurityEventSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    event_type: '',
    entity_type: '',
    risk_level: '',
    user_id: '',
    start_date: undefined as Date | undefined,
    end_date: undefined as Date | undefined,
    include_details: false
  });
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize] = useState(50);
  const { addNotification } = useNotifications();

  const columns = [
    {
      accessorKey: 'timestamp',
      header: 'Timestamp',
      cell: ({ row }: { row: any }) => (
        <div className="text-sm">
          {format(new Date(row.getValue('timestamp')), 'MMM dd, yyyy HH:mm:ss')}
        </div>
      ),
    },
    {
      accessorKey: 'event_type',
      header: 'Event Type',
      cell: ({ row }: { row: any }) => (
        <Badge variant="outline" className="text-xs">
          {row.getValue('event_type')}
        </Badge>
      ),
    },
    {
      accessorKey: 'risk_level',
      header: 'Risk Level',
      cell: ({ row }: { row: any }) => {
        const riskLevel = row.getValue('risk_level') as string;
        return (
          <Badge className={cn('text-xs flex items-center gap-1', getRiskLevelColor(riskLevel))}>
            {getRiskLevelIcon(riskLevel)}
            {riskLevel.toUpperCase()}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'action',
      header: 'Action',
      cell: ({ row }: { row: any }) => (
        <div className="max-w-[200px] truncate text-sm">
          {row.getValue('action')}
        </div>
      ),
    },
    {
      accessorKey: 'entity_type',
      header: 'Entity',
      cell: ({ row }: { row: any }) => (
        <Badge variant="secondary" className="text-xs">
          {row.getValue('entity_type')}
        </Badge>
      ),
    },
    {
      accessorKey: 'source',
      header: 'Source',
      cell: ({ row }: { row: any }) => (
        <div className="text-sm text-muted-foreground">
          {row.getValue('source')}
        </div>
      ),
    },
    {
      accessorKey: 'ip_address',
      header: 'IP Address',
      cell: ({ row }: { row: any }) => (
        <div className="text-xs font-mono">
          {row.getValue('ip_address') || '-'}
        </div>
      ),
    },
    {
      accessorKey: 'description',
      header: 'Description',
      cell: ({ row }: { row: any }) => (
        <div className="max-w-[300px] truncate text-sm">
          {row.getValue('description')}
        </div>
      ),
    },
  ];

  const fetchAuditTrail = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      
      if (filters.event_type) params.append('event_type', filters.event_type);
      if (filters.entity_type) params.append('entity_type', filters.entity_type);
      if (filters.risk_level) params.append('risk_level', filters.risk_level);
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.start_date) params.append('start_date', filters.start_date.toISOString());
      if (filters.end_date) params.append('end_date', filters.end_date.toISOString());
      params.append('include_details', filters.include_details.toString());
      params.append('limit', pageSize.toString());
      params.append('offset', (currentPage * pageSize).toString());

      const response = await api.get(`/audit/trail?${params.toString()}`);
      setAuditData(response.data);
    } catch (error) {
      console.error('Failed to fetch audit trail:', error);
      addNotification({
        title: 'Error',
        message: 'Failed to fetch audit trail data',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchSecurityEvents = async () => {
    try {
      const response = await api.get('/audit/security-events?days=7&risk_level=high');
      setSecurityEvents(response.data);
    } catch (error) {
      console.error('Failed to fetch security events:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      await fetchAuditTrail();
      return;
    }

    setLoading(true);
    try {
      const searchData = {
        query: searchQuery,
        search_fields: ['action', 'description', 'event_type'],
        filters: {
          ...filters,
          include_details: filters.include_details
        },
        limit: pageSize,
        offset: currentPage * pageSize
      };

      const response = await api.post('/audit/search', searchData);
      
      // Convert search response to audit trail format
      setAuditData({
        total_count: response.data.total_matches,
        results: response.data.results,
        limit: pageSize,
        offset: currentPage * pageSize,
        has_more: response.data.total_matches > ((currentPage + 1) * pageSize)
      });
    } catch (error) {
      console.error('Failed to search audit trail:', error);
      addNotification({
        title: 'Error',
        message: 'Failed to search audit trail',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const exportData = {
        start_date: filters.start_date?.toISOString() || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        end_date: filters.end_date?.toISOString() || new Date().toISOString(),
        format: 'json',
        entity_types: filters.entity_type ? [filters.entity_type] : undefined,
        include_sensitive_data: false
      };

      const response = await api.post('/audit/export', exportData);
      
      // Create and download file
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `audit-trail-${format(new Date(), 'yyyy-MM-dd')}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      addNotification({
        title: 'Success',
        message: 'Audit trail exported successfully',
        type: 'success'
      });
    } catch (error) {
      console.error('Failed to export audit trail:', error);
      addNotification({
        title: 'Error',
        message: 'Failed to export audit trail',
        type: 'error'
      });
    }
  };

  const clearFilters = () => {
    setFilters({
      event_type: '',
      entity_type: '',
      risk_level: '',
      user_id: '',
      start_date: undefined,
      end_date: undefined,
      include_details: false
    });
    setSearchQuery('');
    setCurrentPage(0);
  };

  useEffect(() => {
    fetchAuditTrail();
    fetchSecurityEvents();
  }, [currentPage]);

  useEffect(() => {
    if (Object.values(filters).some(v => v)) {
      setCurrentPage(0);
      fetchAuditTrail();
    }
  }, [filters]);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Audit Trail</h1>
          <p className="text-muted-foreground">Monitor and analyze system activity and security events</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleExport} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={() => { fetchAuditTrail(); fetchSecurityEvents(); }} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Security Events Summary */}
      {securityEvents && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Security Events</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{securityEvents.total_security_events}</div>
              <p className="text-xs text-muted-foreground">Last 7 days</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Risk Events</CardTitle>
              <Shield className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{securityEvents.summary.high_risk_events}</div>
              <p className="text-xs text-muted-foreground">Requires attention</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Failed Logins</CardTitle>
              <Eye className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{securityEvents.summary.failed_login_attempts}</div>
              <p className="text-xs text-muted-foreground">Authentication failures</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Config Changes</CardTitle>
              <RefreshCw className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{securityEvents.summary.config_changes}</div>
              <p className="text-xs text-muted-foreground">System modifications</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Filters and Search</CardTitle>
          <CardDescription>Filter audit events by various criteria</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <Label htmlFor="search">Search</Label>
              <div className="flex gap-2">
                <Input
                  id="search"
                  placeholder="Search audit events..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button onClick={handleSearch} size="sm">
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <Label htmlFor="event_type">Event Type</Label>
              <Select value={filters.event_type} onValueChange={(value) => setFilters(prev => ({ ...prev, event_type: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="All events" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All events</SelectItem>
                  <SelectItem value="create">Create</SelectItem>
                  <SelectItem value="update">Update</SelectItem>
                  <SelectItem value="delete">Delete</SelectItem>
                  <SelectItem value="login">Login</SelectItem>
                  <SelectItem value="logout">Logout</SelectItem>
                  <SelectItem value="failed_login_attempt">Failed Login</SelectItem>
                  <SelectItem value="unauthorized_access">Unauthorized Access</SelectItem>
                  <SelectItem value="system_config_changed">Config Change</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="entity_type">Entity Type</Label>
              <Select value={filters.entity_type} onValueChange={(value) => setFilters(prev => ({ ...prev, entity_type: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="All entities" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All entities</SelectItem>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="asset">Asset</SelectItem>
                  <SelectItem value="risk">Risk</SelectItem>
                  <SelectItem value="task">Task</SelectItem>
                  <SelectItem value="assessment">Assessment</SelectItem>
                  <SelectItem value="evidence">Evidence</SelectItem>
                  <SelectItem value="integration">Integration</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="risk_level">Risk Level</Label>
              <Select value={filters.risk_level} onValueChange={(value) => setFilters(prev => ({ ...prev, risk_level: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="All levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All levels</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="user_id">User ID</Label>
              <Input
                id="user_id"
                placeholder="Enter user ID"
                value={filters.user_id}
                onChange={(e) => setFilters(prev => ({ ...prev, user_id: e.target.value }))}
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Start Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !filters.start_date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {filters.start_date ? format(filters.start_date, "PPP") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={filters.start_date}
                    onSelect={(date) => setFilters(prev => ({ ...prev, start_date: date }))}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div>
              <Label>End Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !filters.end_date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {filters.end_date ? format(filters.end_date, "PPP") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={filters.end_date}
                    onSelect={(date) => setFilters(prev => ({ ...prev, end_date: date }))}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="include_details"
                checked={filters.include_details}
                onChange={(e) => setFilters(prev => ({ ...prev, include_details: e.target.checked }))}
                className="rounded"
              />
              <Label htmlFor="include_details">Include event details</Label>
            </div>
            <Button onClick={clearFilters} variant="outline" size="sm">
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Audit Trail Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Audit Events</CardTitle>
              <CardDescription>
                {auditData ? `Showing ${auditData.results.length} of ${auditData.total_count} events` : 'Loading audit events...'}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {auditData && (
            <DataTable
              columns={columns}
              data={auditData.results}
              loading={loading}
              pagination={{
                pageIndex: currentPage,
                pageSize: pageSize,
                pageCount: Math.ceil(auditData.total_count / pageSize),
                onPageChange: setCurrentPage,
                totalItems: auditData.total_count
              }}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}