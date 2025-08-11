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
  Upload,
  RefreshCw,
  Eye,
  Plus
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
              <div className="space-y-6">
                {/* Controls Table */}
                <div className="border rounded-lg">
                  <div className="p-4 border-b">
                    <div className="flex justify-between items-center">
                      <div>
                        <h4 className="font-medium">Assessment Controls</h4>
                        <p className="text-sm text-muted-foreground">Review and evaluate control implementation status</p>
                      </div>
                      <Button variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh Status
                      </Button>
                    </div>
                  </div>
                  
                  <div className="p-4">
                    <div className="grid gap-4">
                      {/* Sample control assessments */}
                      {[
                        { id: 'AC-2', name: 'Account Management', status: 'implemented', score: 85 },
                        { id: 'AC-3', name: 'Access Enforcement', status: 'partially_implemented', score: 65 },
                        { id: 'AU-2', name: 'Audit Events', status: 'not_implemented', score: 20 },
                        { id: 'CM-2', name: 'Baseline Configuration', status: 'implemented', score: 90 }
                      ].map((control) => (
                        <div key={control.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">{control.id}</Badge>
                              <span className="font-medium">{control.name}</span>
                            </div>
                            <Badge 
                              variant={control.status === 'implemented' ? 'default' : 
                                     control.status === 'partially_implemented' ? 'secondary' : 'destructive'}
                            >
                              {control.status.replace('_', ' ').toUpperCase()}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                              <span className="text-sm text-muted-foreground">Score:</span>
                              <Badge variant={control.score >= 80 ? 'default' : control.score >= 60 ? 'secondary' : 'destructive'}>
                                {control.score}%
                              </Badge>
                            </div>
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4 mr-1" />
                              Assess
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Assessment Progress */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Assessment Progress</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">25</div>
                        <div className="text-sm text-muted-foreground">Implemented</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-600">15</div>
                        <div className="text-sm text-muted-foreground">Partial</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">8</div>
                        <div className="text-sm text-muted-foreground">Not Implemented</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">72%</div>
                        <div className="text-sm text-muted-foreground">Overall Score</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
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
              <div className="space-y-6">
                {/* Evidence Upload */}
                <div className="border rounded-lg border-dashed p-6">
                  <div className="text-center">
                    <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Upload Assessment Evidence</h4>
                      <p className="text-sm text-muted-foreground">
                        Support your control assessments with documentation, screenshots, and policies
                      </p>
                    </div>
                    <Button>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Evidence
                    </Button>
                  </div>
                </div>

                {/* Evidence List */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="font-medium">Collected Evidence</h4>
                    <Badge variant="outline">12 Files</Badge>
                  </div>
                  
                  <div className="space-y-3">
                    {[
                      { name: 'Access_Control_Policy_v2.1.pdf', control: 'AC-2', type: 'Policy Document', date: '2025-08-10', status: 'approved' },
                      { name: 'User_Account_Audit_Report.xlsx', control: 'AC-2', type: 'Audit Report', date: '2025-08-09', status: 'pending' },
                      { name: 'RBAC_Configuration_Screenshots.zip', control: 'AC-3', type: 'Screenshots', date: '2025-08-08', status: 'approved' },
                      { name: 'Logging_System_Configuration.json', control: 'AU-2', type: 'Configuration', date: '2025-08-07', status: 'rejected' },
                      { name: 'Baseline_Config_Template.yaml', control: 'CM-2', type: 'Template', date: '2025-08-06', status: 'approved' }
                    ].map((evidence, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                        <div className="flex items-center gap-4">
                          <div className="p-2 bg-muted rounded">
                            <FileText className="h-4 w-4" />
                          </div>
                          <div>
                            <div className="font-medium">{evidence.name}</div>
                            <div className="text-sm text-muted-foreground">
                              Control: {evidence.control} • {evidence.type} • {evidence.date}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant={evidence.status === 'approved' ? 'default' : 
                                   evidence.status === 'pending' ? 'secondary' : 'destructive'}
                          >
                            {evidence.status.toUpperCase()}
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Evidence Summary */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Evidence Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">12</div>
                        <div className="text-sm text-muted-foreground">Total Files</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">8</div>
                        <div className="text-sm text-muted-foreground">Approved</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-600">3</div>
                        <div className="text-sm text-muted-foreground">Pending</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">1</div>
                        <div className="text-sm text-muted-foreground">Rejected</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
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
              <div className="space-y-6">
                {/* Findings Summary */}
                <div className="grid grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl font-bold text-red-600 mb-1">3</div>
                      <div className="text-sm text-muted-foreground">Critical</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl font-bold text-yellow-600 mb-1">7</div>
                      <div className="text-sm text-muted-foreground">Medium</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600 mb-1">5</div>
                      <div className="text-sm text-muted-foreground">Low</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Findings List */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="font-medium">Assessment Findings</h4>
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Finding
                    </Button>
                  </div>
                  
                  <div className="space-y-4">
                    {[
                      {
                        id: 'F-001',
                        title: 'Insufficient Access Control Documentation',
                        control: 'AC-2',
                        severity: 'critical',
                        status: 'open',
                        description: 'Account management procedures lack sufficient detail for compliance requirements.',
                        remediation: 'Update access control policy with detailed procedures and approval workflows.',
                        assignee: 'Security Team',
                        dueDate: '2025-08-20'
                      },
                      {
                        id: 'F-002', 
                        title: 'Audit Log Retention Period Too Short',
                        control: 'AU-2',
                        severity: 'medium',
                        status: 'in_progress',
                        description: 'Current log retention is 30 days, requirement is 90 days minimum.',
                        remediation: 'Configure log management system to retain audit logs for 90 days.',
                        assignee: 'IT Operations',
                        dueDate: '2025-08-15'
                      },
                      {
                        id: 'F-003',
                        title: 'Baseline Configuration Drift',
                        control: 'CM-2',
                        severity: 'medium',
                        status: 'resolved',
                        description: 'Several systems have drifted from approved baseline configurations.',
                        remediation: 'Implement automated configuration management and drift detection.',
                        assignee: 'System Admins',
                        dueDate: '2025-08-10'
                      }
                    ].map((finding) => (
                      <Card key={finding.id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <Badge variant="outline">{finding.id}</Badge>
                              <Badge variant="outline">{finding.control}</Badge>
                              <Badge 
                                variant={finding.severity === 'critical' ? 'destructive' : 
                                       finding.severity === 'medium' ? 'secondary' : 'default'}
                              >
                                {finding.severity.toUpperCase()}
                              </Badge>
                              <Badge 
                                variant={finding.status === 'resolved' ? 'default' :
                                       finding.status === 'in_progress' ? 'secondary' : 'outline'}
                              >
                                {finding.status.replace('_', ' ').toUpperCase()}
                              </Badge>
                            </div>
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </div>
                          
                          <h5 className="font-semibold mb-2">{finding.title}</h5>
                          <p className="text-sm text-muted-foreground mb-3">{finding.description}</p>
                          
                          <div className="border-t pt-3">
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="font-medium">Remediation:</span>
                                <p className="text-muted-foreground mt-1">{finding.remediation}</p>
                              </div>
                              <div>
                                <div className="flex justify-between mb-2">
                                  <span className="font-medium">Assignee:</span>
                                  <span className="text-muted-foreground">{finding.assignee}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-medium">Due Date:</span>
                                  <span className="text-muted-foreground">{finding.dueDate}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
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
              <div className="space-y-6">
                {/* Report Generation */}
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="text-center space-y-4">
                        <FileText className="h-12 w-12 mx-auto text-blue-600" />
                        <div>
                          <h4 className="font-medium mb-2">Executive Summary</h4>
                          <p className="text-sm text-muted-foreground mb-4">
                            High-level overview for leadership and stakeholders
                          </p>
                          <Button className="w-full">
                            <Download className="h-4 w-4 mr-2" />
                            Generate Report
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="text-center space-y-4">
                        <Shield className="h-12 w-12 mx-auto text-green-600" />
                        <div>
                          <h4 className="font-medium mb-2">Technical Details</h4>
                          <p className="text-sm text-muted-foreground mb-4">
                            Comprehensive technical findings and recommendations
                          </p>
                          <Button className="w-full" variant="outline">
                            <Download className="h-4 w-4 mr-2" />
                            Generate Report
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Report Templates */}
                <div>
                  <h4 className="font-medium mb-4">Available Report Templates</h4>
                  <div className="space-y-3">
                    {[
                      { name: 'NIST CSF Assessment Report', description: 'Comprehensive assessment aligned with NIST Cybersecurity Framework', format: 'PDF' },
                      { name: 'SOC 2 Type II Report', description: 'Service organization control report for compliance', format: 'PDF' },
                      { name: 'ISO 27001 Gap Analysis', description: 'Gap analysis against ISO 27001 standard requirements', format: 'Excel' },
                      { name: 'Executive Dashboard', description: 'Visual summary for executive leadership', format: 'PowerPoint' },
                      { name: 'Remediation Action Plan', description: 'Detailed remediation roadmap with timelines', format: 'Excel' }
                    ].map((template, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                        <div className="flex items-center gap-4">
                          <div className="p-2 bg-muted rounded">
                            <FileText className="h-4 w-4" />
                          </div>
                          <div>
                            <div className="font-medium">{template.name}</div>
                            <div className="text-sm text-muted-foreground">{template.description}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{template.format}</Badge>
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            Generate
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Generated Reports History */}
                <div>
                  <h4 className="font-medium mb-4">Recently Generated Reports</h4>
                  <div className="space-y-3">
                    {[
                      { name: 'NIST_CSF_Assessment_Q3_2025.pdf', date: '2025-08-10', size: '2.3 MB', status: 'completed' },
                      { name: 'SOC2_Remediation_Plan_v1.2.xlsx', date: '2025-08-08', size: '856 KB', status: 'completed' },
                      { name: 'Executive_Summary_Aug2025.pptx', date: '2025-08-05', size: '1.8 MB', status: 'completed' }
                    ].map((report, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                        <div className="flex items-center gap-4">
                          <div className="p-2 bg-muted rounded">
                            <FileText className="h-4 w-4" />
                          </div>
                          <div>
                            <div className="font-medium">{report.name}</div>
                            <div className="text-sm text-muted-foreground">
                              Generated on {report.date} • {report.size}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="default">
                            {report.status.toUpperCase()}
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}