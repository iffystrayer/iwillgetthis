import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Brain, 
  TrendingUp, 
  ChevronDown, 
  ChevronUp, 
  Lightbulb,
  AlertTriangle,
  CheckCircle2,
  Eye
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface AIInsight {
  id: number;
  insight_type: string;
  title: string;
  summary: string;
  detailed_analysis?: string;
  relevance_score: number;
  confidence_score: number;
  impact_score: number;
  recommendations?: string[];
  generated_at: string;
  category?: string;
}

interface AIInsightCardProps {
  insight: AIInsight;
  compact?: boolean;
  showActions?: boolean;
  onView?: (insight: AIInsight) => void;
  onDismiss?: (insightId: number) => void;
  className?: string;
}

export const AIInsightCard: React.FC<AIInsightCardProps> = ({
  insight,
  compact = false,
  showActions = true,
  onView,
  onDismiss,
  className
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getInsightTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'trend_analysis':
        return <TrendingUp className="w-4 h-4" />;
      case 'risk_prediction':
        return <AlertTriangle className="w-4 h-4" />;
      case 'optimization':
        return <Lightbulb className="w-4 h-4" />;
      default:
        return <Brain className="w-4 h-4" />;
    }
  };

  const getInsightTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'trend_analysis':
        return 'bg-blue-100 text-blue-800';
      case 'risk_prediction':
        return 'bg-red-100 text-red-800';
      case 'optimization':
        return 'bg-green-100 text-green-800';
      case 'anomaly':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-purple-100 text-purple-800';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (compact) {
    return (
      <div className={cn("border rounded-lg p-3 bg-white hover:bg-gray-50 transition-colors", className)}>
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1">
            <div className={cn("p-1 rounded", getInsightTypeColor(insight.insight_type))}>
              {getInsightTypeIcon(insight.insight_type)}
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-sm line-clamp-1">{insight.title}</h4>
              <p className="text-xs text-gray-600 line-clamp-2 mt-1">{insight.summary}</p>
              <div className="flex items-center space-x-2 mt-2">
                <Badge variant="outline" className="text-xs">
                  {insight.insight_type.replace('_', ' ')}
                </Badge>
                <span className={cn("text-xs font-medium", getScoreColor(insight.impact_score))}>
                  {(insight.impact_score * 100).toFixed(0)}% impact
                </span>
              </div>
            </div>
          </div>
          {showActions && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onView?.(insight)}
              className="ml-2"
            >
              <Eye className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <div className={cn("p-2 rounded-lg", getInsightTypeColor(insight.insight_type))}>
              {getInsightTypeIcon(insight.insight_type)}
            </div>
            <div>
              <CardTitle className="text-lg">{insight.title}</CardTitle>
              <CardDescription className="mt-1">
                Generated on {new Date(insight.generated_at).toLocaleDateString()}
                {insight.category && ` • ${insight.category}`}
              </CardDescription>
            </div>
          </div>
          <Badge className={getInsightTypeColor(insight.insight_type)}>
            {insight.insight_type.replace('_', ' ')}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Summary */}
        <div>
          <p className="text-sm text-gray-700">{insight.summary}</p>
        </div>

        {/* Scores */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-600">Relevance</span>
              <span className={cn("text-sm font-semibold", getScoreColor(insight.relevance_score))}>
                {(insight.relevance_score * 100).toFixed(0)}%
              </span>
            </div>
            <Progress value={insight.relevance_score * 100} className="h-2" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-600">Confidence</span>
              <span className={cn("text-sm font-semibold", getScoreColor(insight.confidence_score))}>
                {(insight.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
            <Progress value={insight.confidence_score * 100} className="h-2" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-600">Impact</span>
              <span className={cn("text-sm font-semibold", getScoreColor(insight.impact_score))}>
                {(insight.impact_score * 100).toFixed(0)}%
              </span>
            </div>
            <Progress value={insight.impact_score * 100} className="h-2" />
          </div>
        </div>

        {/* Detailed Analysis (expandable) */}
        {insight.detailed_analysis && (
          <div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-auto p-0 font-medium text-blue-600 hover:text-blue-800"
            >
              <span className="mr-1">
                {isExpanded ? 'Hide' : 'Show'} detailed analysis
              </span>
              {isExpanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>
            {isExpanded && (
              <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-700">{insight.detailed_analysis}</p>
              </div>
            )}
          </div>
        )}

        {/* Recommendations */}
        {insight.recommendations && insight.recommendations.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
              <CheckCircle2 className="w-4 h-4 mr-1 text-green-600" />
              Recommendations
            </h4>
            <ul className="space-y-1">
              {insight.recommendations.map((rec, index) => (
                <li key={index} className="text-sm text-gray-700 flex items-start">
                  <span className="mr-2 text-green-600">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Actions */}
        {showActions && (
          <div className="flex justify-between pt-2 border-t">
            <div className="flex space-x-2">
              {onView && (
                <Button variant="outline" size="sm" onClick={() => onView(insight)}>
                  <Eye className="w-4 h-4 mr-1" />
                  View Details
                </Button>
              )}
            </div>
            {onDismiss && (
              <Button variant="ghost" size="sm" onClick={() => onDismiss(insight.id)}>
                Dismiss
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AIInsightCard;