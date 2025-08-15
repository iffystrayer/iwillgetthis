import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Brain, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AIPredictionBadgeProps {
  prediction?: {
    predicted_value: number;
    confidence_level: 'high' | 'medium' | 'low';
    risk_level: string;
    trend?: 'increasing' | 'decreasing' | 'stable';
  };
  entityType: string;
  entityId: number;
  className?: string;
  compact?: boolean;
}

export const AIPredictionBadge: React.FC<AIPredictionBadgeProps> = ({
  prediction,
  entityType,
  entityId,
  className,
  compact = false
}) => {
  if (!prediction) {
    return (
      <Badge variant="outline" className={cn("text-xs", className)}>
        <Brain className="w-3 h-3 mr-1" />
        {compact ? "No AI" : "No AI Prediction"}
      </Badge>
    );
  }

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getConfidenceColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="w-3 h-3 text-red-500" />;
      case 'decreasing':
        return <TrendingDown className="w-3 h-3 text-green-500" />;
      default:
        return null;
    }
  };

  if (compact) {
    return (
      <div className={cn("flex items-center space-x-1", className)}>
        <Badge className={getRiskLevelColor(prediction.risk_level)}>
          <Brain className="w-3 h-3 mr-1" />
          {prediction.predicted_value.toFixed(1)}
        </Badge>
        {prediction.trend && getTrendIcon(prediction.trend)}
      </div>
    );
  }

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <Badge className={getRiskLevelColor(prediction.risk_level)}>
        <Brain className="w-3 h-3 mr-1" />
        AI: {prediction.predicted_value.toFixed(1)} ({prediction.risk_level})
      </Badge>
      <Badge variant="outline" className={getConfidenceColor(prediction.confidence_level)}>
        {prediction.confidence_level} confidence
      </Badge>
      {prediction.trend && (
        <div className="flex items-center">
          {getTrendIcon(prediction.trend)}
        </div>
      )}
    </div>
  );
};

export default AIPredictionBadge;