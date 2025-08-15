import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  Brain,
  AlertTriangle,
  RefreshCw,
  Download,
  Filter,
  Activity,
  Target,
  Zap,
  BarChart3,
  Clock,
  CheckCircle2,
  XCircle,
  Eye
} from 'lucide-react';
import { aiAnalyticsApi } from '../../lib/api';

// Types for AI Analytics
interface AIModel {
  id: number;
  name: string;
  model_type: string;
  algorithm: string;
  status: string;
  accuracy_score?: number;
  precision_score?: number;
  recall_score?: number;
  f1_score?: number;
  trained_at?: string;
  is_production: boolean;
}

interface AIPrediction {
  id: number;
  model_id: number;
  entity_type: string;
  entity_id: number;
  predicted_value: number;
  confidence_score: number;
  confidence_level: string;
  risk_level: string;
  prediction_date: string;
  prediction_reason: string;
}

interface AIAlert {
  id: number;
  alert_type: string;
  title: string;
  severity: string;
  status: string;
  confidence_score: number;
  first_detected_at: string;
  affected_entity_type: string;
  affected_entity_id: number;
}

interface AIInsight {
  id: number;
  insight_type: string;
  title: string;
  summary: string;
  relevance_score: number;
  confidence_score: number;
  impact_score: number;
  generated_at: string;
  recommendations: string[];
}

interface AnalyticsDashboard {
  summary: {
    total_models: number;
    active_models: number;
    total_predictions: number;
    active_alerts: number;
    model_accuracy_avg: number;
  };
  model_performance_overview: Array<{
    model_id: number;
    model_name: string;
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
  }>;
  recent_predictions: AIPrediction[];
  active_alerts: AIAlert[];
  trending_insights: AIInsight[];
}

const PredictiveAnalyticsPage: React.FC = () => {
  const [dashboard, setDashboard] = useState<AnalyticsDashboard | null>(null);
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const [dashboardResponse, modelsResponse] = await Promise.all([
        aiAnalyticsApi.getDashboard(),
        aiAnalyticsApi.getModels()
      ]);
      setDashboard(dashboardResponse);
      setModels(modelsResponse);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch AI analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 120000); // Refresh every 2 minutes
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'bg-green-500';
      case 'training': return 'bg-blue-500';
      case 'testing': return 'bg-yellow-500';
      case 'failed': return 'bg-red-500';
      case 'deprecated': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      case 'info': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  const getConfidenceBadge = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center space-x-2 mb-6">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <span>Loading Predictive Analytics...</span>
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
        <Button onClick={fetchDashboard}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>No analytics data available</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Predictive Analytics</h1>
          <p className="text-gray-600 mt-1">AI-powered risk prediction and insights</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={fetchDashboard} size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Models</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard.summary.total_models}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {dashboard.summary.active_models} active
                </p>
              </div>
              <Brain className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Predictions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard.summary.total_predictions.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {dashboard.recent_predictions.length} recent
                </p>
              </div>
              <Target className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard.summary.active_alerts}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Require attention
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Accuracy</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(dashboard.summary.model_accuracy_avg * 100).toFixed(1)}%
                </p>
                <div className="mt-2">
                  <Progress value={dashboard.summary.model_accuracy_avg * 100} className="h-2" />
                </div>
              </div>
              <BarChart3 className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Insights</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard.trending_insights.length}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  New insights available
                </p>
              </div>
              <Eye className="h-8 w-8 text-indigo-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="models">Models</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Model Performance */}
            <Card>
              <CardHeader>
                <CardTitle>Model Performance</CardTitle>
                <CardDescription>Top performing AI models</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboard.model_performance_overview.slice(0, 5).map((model) => (
                    <div key={model.model_id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{model.model_name}</h4>
                        <p className="text-sm text-gray-600">
                          Accuracy: {(model.accuracy * 100).toFixed(1)}% | 
                          F1-Score: {(model.f1_score * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div className="text-right">
                        <Progress value={model.accuracy * 100} className="h-2 w-20" />
                        <p className="text-xs text-gray-500 mt-1">
                          {(model.accuracy * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Predictions */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Predictions</CardTitle>
                <CardDescription>Latest AI predictions and assessments</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {dashboard.recent_predictions.slice(0, 5).map((prediction) => (
                    <div key={prediction.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium">
                          {prediction.entity_type} #{prediction.entity_id}
                        </h4>
                        <p className="text-sm text-gray-600">
                          Risk Score: {prediction.predicted_value.toFixed(1)} 
                          <Badge className={`ml-2 ${getConfidenceBadge(prediction.confidence_level)}`}>
                            {prediction.confidence_level}
                          </Badge>
                        </p>
                      </div>
                      <div className="text-right">
                        <Badge variant={prediction.risk_level === 'high' ? 'destructive' : 'secondary'}>
                          {prediction.risk_level}
                        </Badge>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(prediction.prediction_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="models" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Models</CardTitle>
              <CardDescription>Manage and monitor your predictive models</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {models.map((model) => (
                  <div key={model.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(model.status)}`} />
                        <h3 className="font-medium">{model.name}</h3>
                        <Badge variant={model.is_production ? 'default' : 'secondary'}>
                          {model.is_production ? 'Production' : 'Development'}
                        </Badge>
                      </div>
                      <Badge variant="outline">{model.status}</Badge>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600 mb-1">Model Type</p>
                        <p className="font-semibold">{model.model_type.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Algorithm</p>
                        <p className="font-semibold">{model.algorithm}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Accuracy</p>
                        <p className="font-semibold">
                          {model.accuracy_score ? `${(model.accuracy_score * 100).toFixed(1)}%` : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Last Trained</p>
                        <p className="font-semibold">
                          {model.trained_at ? new Date(model.trained_at).toLocaleDateString() : 'Never'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Predictions</CardTitle>
              <CardDescription>Review and validate predictions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboard.recent_predictions.map((prediction) => (
                  <div key={prediction.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-medium">
                          {prediction.entity_type} #{prediction.entity_id}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Predicted on {new Date(prediction.prediction_date).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <Badge variant={prediction.risk_level === 'high' ? 'destructive' : 'secondary'}>
                          {prediction.risk_level} risk
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600 mb-1">Predicted Value</p>
                        <p className="font-semibold text-lg">{prediction.predicted_value.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Confidence</p>
                        <div className="flex items-center space-x-2">
                          <Progress value={prediction.confidence_score * 100} className="h-2 flex-1" />
                          <span className="font-semibold">{(prediction.confidence_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Confidence Level</p>
                        <Badge className={getConfidenceBadge(prediction.confidence_level)}>
                          {prediction.confidence_level}
                        </Badge>
                      </div>
                    </div>
                    
                    {prediction.prediction_reason && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm font-medium text-gray-800 mb-1">Reasoning:</p>
                        <p className="text-sm text-gray-600">{prediction.prediction_reason}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Alerts</CardTitle>
              <CardDescription>AI-generated alerts requiring attention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboard.active_alerts.map((alert) => (
                  <div key={alert.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${getSeverityColor(alert.severity)}`} />
                        <h3 className="font-medium">{alert.title}</h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getSeverityColor(alert.severity)}>
                          {alert.severity}
                        </Badge>
                        <Badge variant="outline">{alert.status}</Badge>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600 mb-1">Alert Type</p>
                        <p className="font-semibold">{alert.alert_type.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Affected Entity</p>
                        <p className="font-semibold">
                          {alert.affected_entity_type} #{alert.affected_entity_id}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Confidence</p>
                        <p className="font-semibold">{(alert.confidence_score * 100).toFixed(0)}%</p>
                      </div>
                    </div>
                    
                    <div className="mt-3 text-xs text-gray-500">
                      Detected: {new Date(alert.first_detected_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Insights</CardTitle>
              <CardDescription>AI-generated insights and recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboard.trending_insights.map((insight) => (
                  <div key={insight.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-medium">{insight.title}</h3>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{insight.insight_type}</Badge>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">{insight.summary}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-3">
                      <div>
                        <p className="text-gray-600 mb-1">Relevance</p>
                        <div className="flex items-center space-x-2">
                          <Progress value={insight.relevance_score * 100} className="h-2 flex-1" />
                          <span className="font-semibold">{(insight.relevance_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Confidence</p>
                        <div className="flex items-center space-x-2">
                          <Progress value={insight.confidence_score * 100} className="h-2 flex-1" />
                          <span className="font-semibold">{(insight.confidence_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Impact</p>
                        <div className="flex items-center space-x-2">
                          <Progress value={insight.impact_score * 100} className="h-2 flex-1" />
                          <span className="font-semibold">{(insight.impact_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                    
                    {insight.recommendations && insight.recommendations.length > 0 && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm font-medium text-blue-800 mb-2">Recommendations:</p>
                        <ul className="text-sm text-blue-700 space-y-1">
                          {insight.recommendations.map((rec, idx) => (
                            <li key={idx} className="flex items-start space-x-2">
                              <span>•</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    <div className="mt-3 text-xs text-gray-500">
                      Generated: {new Date(insight.generated_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PredictiveAnalyticsPage;