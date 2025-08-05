import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Shield, 
  ArrowLeft, 
  Calendar, 
  User, 
  FileText, 
  CheckCircle, 
  Clock, 
  AlertTriangle,
  Edit,
  Download,
  Upload
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { assessmentsApi } from '@/lib/api';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

export default function AssessmentDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssessment = async () => {
      if (!id) {
        setError('Assessment ID not provided');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await assessmentsApi.getById(id);
        setAssessment(response);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch assessment details');
        console.error('Error fetching assessment:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAssessment();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/assessments')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Assessments
          </Button>
        </div>
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive mb-2">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">Error Loading Assessment</span>
            </div>
            <p>{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/assessments')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Assessments
          </Button>
        </div>
        <Card>
          <CardContent className="pt-6">
            <p>Assessment not found</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'default';
      case 'in progress': return 'secondary';
      case 'planning': return 'outline';
      case 'on hold': return 'destructive';
      default: return 'secondary';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'in progress': return <Clock className="h-4 w-4" />;
      case 'planning': return <FileText className="h-4 w-4" />;
      case 'on hold': return <AlertTriangle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/assessments')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Assessments
          </Button>
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Shield className="h-8 w-8" />
              {assessment.name}
            </h1>
            <p className="text-muted-foreground">
              {assessment.framework} • {assessment.type || 'Assessment'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Status</CardTitle>
            {getStatusIcon(assessment.status)}
          </CardHeader>
          <CardContent>
            <Badge variant={getStatusColor(assessment.status)} className="mb-2">
              {assessment.status || 'Unknown'}
            </Badge>
            <p className="text-xs text-muted-foreground">
              Progress: {assessment.progress || 0}%
            </p>
            <Progress value={assessment.progress || 0} className="mt-2" />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Due Date</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assessment.due_date ? new Date(assessment.due_date).toLocaleDateString() : 'Not set'}
            </div>
            <p className="text-xs text-muted-foreground">
              {assessment.due_date && new Date(assessment.due_date) < new Date() 
                ? 'Overdue' 
                : 'On schedule'
              }
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Lead Assessor</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assessment.assessor || 'Unassigned'}
            </div>
            <p className="text-xs text-muted-foreground">
              Primary contact
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Framework</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold">
              {assessment.framework}
            </div>
            <p className="text-xs text-muted-foreground">
              Compliance standard
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Content */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="controls">Controls</TabsTrigger>
          <TabsTrigger value="evidence">Evidence</TabsTrigger>
          <TabsTrigger value="findings">Findings</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Assessment Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-muted-foreground">Description:</span>
                  <p className="mt-1">{assessment.description || 'No description provided'}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-muted-foreground">Scope:</span>
                  <p className="mt-1">{assessment.scope || 'No scope defined'}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-muted-foreground">Created:</span>
                  <p className="mt-1">
                    {assessment.created_date 
                      ? new Date(assessment.created_date).toLocaleDateString() 
                      : 'Unknown'
                    }
                  </p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span>Assessment created</span>
                    <span className="text-muted-foreground ml-auto">
                      {assessment.created_date 
                        ? new Date(assessment.created_date).toLocaleDateString() 
                        : 'Unknown'
                      }
                    </span>
                  </div>
                  <div className="text-center py-4 text-muted-foreground text-sm">
                    More activity will appear here as the assessment progresses
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="controls" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Control Assessment</CardTitle>
              <CardDescription>
                Framework controls and their assessment status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Control assessment functionality coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="evidence" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Evidence Collection</CardTitle>
              <CardDescription>
                Supporting documentation and evidence for controls
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Upload className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Evidence management functionality coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="findings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Assessment Findings</CardTitle>
              <CardDescription>
                Issues, gaps, and recommendations identified during assessment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Findings tracking functionality coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Assessment Reports</CardTitle>
              <CardDescription>
                Generated reports and documentation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Report generation functionality coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}