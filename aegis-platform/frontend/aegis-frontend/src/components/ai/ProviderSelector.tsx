import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { CheckCircle, AlertTriangle, XCircle, Zap } from 'lucide-react';
import { aiApi } from '../../lib/api';
import { ProvidersStatus, RecommendedProviderResponse } from '../../types/ai';

interface ProviderSelectorProps {
  taskType?: string;
  selectedProvider?: string;
  onProviderChange: (provider: string | undefined) => void;
  className?: string;
}

// Remove duplicate interface - using the one from types/ai.ts

const ProviderSelector: React.FC<ProviderSelectorProps> = ({
  taskType = 'general',
  selectedProvider,
  onProviderChange,
  className = ''
}) => {
  const [providers, setProviders] = useState<ProvidersStatus>({});
  const [recommendedProvider, setRecommendedProvider] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setLoading(true);
        const [statusResponse, recommendedResponse] = await Promise.all([
          aiApi.getProvidersStatus(),
          aiApi.getRecommendedProvider(taskType)
        ]);
        
        setProviders(statusResponse as ProvidersStatus);
        setRecommendedProvider((recommendedResponse as RecommendedProviderResponse).recommended_provider);
      } catch (error) {
        console.error('Failed to fetch provider data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProviders();
  }, [taskType]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-3 w-3 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="h-3 w-3 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="h-3 w-3 text-red-500" />;
      default:
        return <AlertTriangle className="h-3 w-3 text-gray-500" />;
    }
  };

  const formatProviderName = (name: string) => {
    return name.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const enabledProviders = Object.entries(providers)
    .filter(([_, provider]) => provider.enabled)
    .sort((a, b) => {
      // Sort by: recommended first, then by success rate
      if (a[0] === recommendedProvider) return -1;
      if (b[0] === recommendedProvider) return 1;
      return b[1].success_rate - a[1].success_rate;
    });

  if (loading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="animate-pulse bg-gray-200 h-9 w-48 rounded-md" />
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">
          AI Provider
        </label>
        {recommendedProvider && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onProviderChange(recommendedProvider)}
            className="text-xs h-6 px-2"
          >
            <Zap className="h-3 w-3 mr-1" />
            Use Recommended
          </Button>
        )}
      </div>
      
      <Select value={selectedProvider || ''} onValueChange={(value) => onProviderChange(value || undefined)}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Auto-select provider" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="">
            <div className="flex items-center space-x-2">
              <Zap className="h-3 w-3 text-blue-500" />
              <span>Auto-select (Recommended)</span>
            </div>
          </SelectItem>
          {enabledProviders.map(([providerName, provider]) => (
            <SelectItem key={providerName} value={providerName}>
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(provider.status)}
                  <span>{formatProviderName(providerName)}</span>
                  {providerName === recommendedProvider && (
                    <Badge variant="secondary" className="text-xs">
                      Recommended
                    </Badge>
                  )}
                </div>
                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  <span>{provider.success_rate.toFixed(0)}%</span>
                  <span>{provider.avg_response_time.toFixed(1)}s</span>
                </div>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {selectedProvider && providers[selectedProvider] && (
        <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
          <div className="flex items-center justify-between">
            <span>Selected: {formatProviderName(selectedProvider)}</span>
            <div className="flex items-center space-x-2">
              {getStatusIcon(providers[selectedProvider].status)}
              <span>{providers[selectedProvider].success_rate.toFixed(0)}% success</span>
              <span>{providers[selectedProvider].avg_response_time.toFixed(1)}s avg</span>
            </div>
          </div>
        </div>
      )}
      
      {!selectedProvider && recommendedProvider && (
        <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded">
          <div className="flex items-center space-x-1">
            <Zap className="h-3 w-3" />
            <span>Will use {formatProviderName(recommendedProvider)} (recommended for {taskType})</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProviderSelector;