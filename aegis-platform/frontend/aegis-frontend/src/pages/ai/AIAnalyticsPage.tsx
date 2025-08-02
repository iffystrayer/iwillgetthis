import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Clock, 
  Activity, 
  Brain,
  AlertTriangle,
  RefreshCw,
  Download,
  Filter
} from 'lucide-react';
import { aiApi } from '../../lib/api';
import { UsageSummary } from '../../types/ai';

// Using UsageSummary from types/ai.ts

const AIAnalyticsPage: React.FC = () => {
  const [usageSummary, setUsageSummary] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('7d');

  const fetchUsageSummary = async () => {
    try {
      setLoading(true);
      const response = await aiApi.getUsageSummary();
      setUsageSummary(response as UsageSummary);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch AI analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsageSummary();
    const interval = setInterval(fetchUsageSummary, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const formatProviderName = (name: string) => {
    return name.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const getProviderColor = (index: number) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500', 
      'bg-purple-500',
      'bg-orange-500',
      'bg-red-500',
      'bg-indigo-500',
      'bg-pink-500',
      'bg-yellow-500'
    ];
    return colors[index % colors.length];
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center space-x-2 mb-6">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <span>Loading AI Analytics...</span>
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
        <Button onClick={fetchUsageSummary}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  if (!usageSummary) {
    return (
      <div className="p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>No usage data available</AlertDescription>
        </Alert>
      </div>
    );
  }

  const enabledProviders = Object.entries(usageSummary.provider_breakdown)
    .filter(([_, provider]) => provider.enabled)
    .sort((a, b) => b[1].requests_count - a[1].requests_count);

  const costPerRequest = usageSummary.total_requests > 0 
    ? usageSummary.total_cost / usageSummary.total_requests 
    : 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Analytics</h1>
          <p className="text-gray-600 mt-1">Monitor AI usage, costs, and performance</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={fetchUsageSummary} size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Requests</p>
                <p className="text-2xl font-bold text-gray-900">
                  {usageSummary.total_requests.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Across {usageSummary.active_providers} providers
                </p>
              </div>
              <Activity className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Cost</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${usageSummary.total_cost.toFixed(4)}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  ${costPerRequest.toFixed(6)} per request
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {usageSummary.average_success_rate.toFixed(1)}%
                </p>
                <div className="mt-2">
                  <Progress value={usageSummary.average_success_rate} className="h-2" />
                </div>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Providers</p>
                <p className="text-2xl font-bold text-gray-900">
                  {usageSummary.active_providers}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {Object.keys(usageSummary.provider_breakdown).length} total configured
                </p>
              </div>
              <Brain className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Provider Performance Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Provider Performance</CardTitle>
          <CardDescription>
            Compare performance metrics across all AI providers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {enabledProviders.map(([providerName, provider], index) => {
              const requestPercentage = usageSummary.total_requests > 0 
                ? (provider.requests_count / usageSummary.total_requests) * 100 
                : 0;
              const costPercentage = usageSummary.total_cost > 0 
                ? (provider.total_cost / usageSummary.total_cost) * 100 
                : 0;

              return (
                <div key={providerName} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${getProviderColor(index)}`} />
                      <span className="font-medium">{formatProviderName(providerName)}</span>
                      <Badge 
                        variant={provider.status === 'healthy' ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {provider.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-600">
                      {provider.requests_count} requests
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600 mb-1">Request Share</p>
                      <p className="font-semibold">{requestPercentage.toFixed(1)}%</p>
                      <Progress value={requestPercentage} className="h-2 mt-1" />
                    </div>
                    <div>
                      <p className="text-gray-600 mb-1">Cost Share</p>
                      <p className="font-semibold">{costPercentage.toFixed(1)}%</p>
                      <p className="text-xs text-gray-500">${provider.total_cost.toFixed(4)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600 mb-1">Success Rate</p>
                      <p className="font-semibold">{provider.success_rate.toFixed(1)}%</p>
                      <Progress value={provider.success_rate} className="h-2 mt-1" />
                    </div>
                    <div>
                      <p className="text-gray-600 mb-1">Avg Response Time</p>
                      <p className="font-semibold">{provider.avg_response_time.toFixed(2)}s</p>
                      {provider.avg_response_time > 5 && (
                        <p className="text-xs text-yellow-600">⚠ Slow</p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Cost Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Cost Breakdown</CardTitle>
            <CardDescription>Spending by provider</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {enabledProviders.map(([providerName, provider], index) => {
                const costPercentage = usageSummary.total_cost > 0 
                  ? (provider.total_cost / usageSummary.total_cost) * 100 
                  : 0;
                
                return (
                  <div key={providerName} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${getProviderColor(index)}`} />
                      <span className="text-sm font-medium">
                        {formatProviderName(providerName)}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">${provider.total_cost.toFixed(4)}</p>
                      <p className="text-xs text-gray-500">{costPercentage.toFixed(1)}%</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Request Volume</CardTitle>
            <CardDescription>Requests by provider</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {enabledProviders.map(([providerName, provider], index) => {
                const requestPercentage = usageSummary.total_requests > 0 
                  ? (provider.requests_count / usageSummary.total_requests) * 100 
                  : 0;
                
                return (
                  <div key={providerName} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${getProviderColor(index)}`} />
                      <span className="text-sm font-medium">
                        {formatProviderName(providerName)}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">{provider.requests_count}</p>
                      <p className="text-xs text-gray-500">{requestPercentage.toFixed(1)}%</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AIAnalyticsPage;