import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  RefreshCw, 
  Settings, 
  Activity,
  DollarSign,
  Clock,
  Zap,
  Brain
} from 'lucide-react';
import { aiApi } from '../../lib/api';
import { ProvidersStatus, ProviderTestResponse } from '../../types/ai';

// Using interfaces from types/ai.ts

const ProvidersPage: React.FC = () => {
  const [providersStatus, setProvidersStatus] = useState<ProvidersStatus>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingProvider, setTestingProvider] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<{[key: string]: ProviderTestResponse}>({});

  const fetchProvidersStatus = async () => {
    try {
      setLoading(true);
      const response = await aiApi.getProvidersStatus();
      setProvidersStatus(response as ProvidersStatus);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch providers status');
    } finally {
      setLoading(false);
    }
  };

  const testProvider = async (providerName: string) => {
    try {
      setTestingProvider(providerName);
      const response = await aiApi.testProvider(providerName, "Hello, this is a test message for the AI provider.");
      setTestResults(prev => ({ ...prev, [providerName]: response as ProviderTestResponse }));
    } catch (err: any) {
      setTestResults(prev => ({ 
        ...prev, 
        [providerName]: { 
          test_successful: false, 
          provider_used: providerName,
          response: '',
          response_time: 0,
          cost: 0,
          timestamp: new Date().toISOString(),
          error: err.response?.data?.detail || 'Test failed' 
        } as ProviderTestResponse
      }));
    } finally {
      setTestingProvider(null);
    }
  };

  useEffect(() => {
    fetchProvidersStatus();
    const interval = setInterval(fetchProvidersStatus, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800';
      case 'unhealthy':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatProviderName = (name: string) => {
    return name.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center space-x-2 mb-6">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <span>Loading AI Providers...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button onClick={fetchProvidersStatus}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  const enabledProviders = Object.entries(providersStatus).filter(([_, status]) => status.enabled);
  const totalRequests = Object.values(providersStatus).reduce((sum, status) => sum + status.requests_count, 0);
  const totalCost = Object.values(providersStatus).reduce((sum, status) => sum + status.total_cost, 0);
  const avgSuccessRate = enabledProviders.length > 0 
    ? enabledProviders.reduce((sum, [_, status]) => sum + status.success_rate, 0) / enabledProviders.length
    : 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Providers</h1>
          <p className="text-gray-600 mt-1">Manage and monitor LLM providers</p>
        </div>
        <Button onClick={fetchProvidersStatus} size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Providers</p>
                <p className="text-2xl font-bold text-gray-900">{enabledProviders.length}</p>
              </div>
              <Brain className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Requests</p>
                <p className="text-2xl font-bold text-gray-900">{totalRequests.toLocaleString()}</p>
              </div>
              <Activity className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Cost</p>
                <p className="text-2xl font-bold text-gray-900">${totalCost.toFixed(4)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">{avgSuccessRate.toFixed(1)}%</p>
              </div>
              <Zap className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Providers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Object.entries(providersStatus).map(([providerName, status]) => (
          <Card key={providerName} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(status.status)}
                  <div>
                    <CardTitle className="text-lg">{formatProviderName(providerName)}</CardTitle>
                    <CardDescription>
                      <Badge className={getStatusColor(status.status)} variant="secondary">
                        {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
                      </Badge>
                    </CardDescription>
                  </div>
                </div>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => testProvider(providerName)}
                  disabled={testingProvider === providerName || !status.enabled}
                >
                  {testingProvider === providerName ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    'Test'
                  )}
                </Button>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Requests</p>
                  <p className="font-semibold">{status.requests_count.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-600">Success Rate</p>
                  <p className="font-semibold">{status.success_rate.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-600">Avg Response</p>
                  <p className="font-semibold">{status.avg_response_time.toFixed(2)}s</p>
                </div>
                <div>
                  <p className="text-gray-600">Total Cost</p>
                  <p className="font-semibold">${status.total_cost.toFixed(4)}</p>
                </div>
              </div>

              {/* Success Rate Progress */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Success Rate</span>
                  <span>{status.success_rate.toFixed(1)}%</span>
                </div>
                <Progress value={status.success_rate} className="h-2" />
              </div>

              {/* Capabilities */}
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">Capabilities</p>
                <div className="flex flex-wrap gap-1">
                  {status.capabilities.supports_streaming && (
                    <Badge variant="outline" className="text-xs">Streaming</Badge>
                  )}
                  {status.capabilities.supports_function_calling && (
                    <Badge variant="outline" className="text-xs">Functions</Badge>
                  )}
                  {status.capabilities.supports_vision && (
                    <Badge variant="outline" className="text-xs">Vision</Badge>
                  )}
                  {status.capabilities.supports_json_mode && (
                    <Badge variant="outline" className="text-xs">JSON Mode</Badge>
                  )}
                  <Badge variant="outline" className="text-xs">
                    {(status.capabilities.max_context_length / 1000).toFixed(0)}K tokens
                  </Badge>
                </div>
              </div>

              {/* Test Results */}
              {testResults[providerName] && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium mb-2">Latest Test Result</p>
                  {testResults[providerName].test_successful ? (
                    <div className="space-y-1 text-xs">
                      <p className="text-green-600">✓ Test successful</p>
                      <p>Response time: {testResults[providerName].response_time?.toFixed(2)}s</p>
                      <p>Cost: ${testResults[providerName].cost?.toFixed(6) || '0.000000'}</p>
                      <p className="text-gray-600 truncate">{testResults[providerName].response}</p>
                    </div>
                  ) : (
                    <p className="text-xs text-red-600">✗ {testResults[providerName].error}</p>
                  )}
                </div>
              )}

              {/* Daily Usage */}
              {status.cost_tracking && (
                <div className="text-xs text-gray-600">
                  <p>Today: {status.cost_tracking.daily_requests} requests, ${status.cost_tracking.daily_cost.toFixed(4)}</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ProvidersPage;