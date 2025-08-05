import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Plus, Filter, Calendar, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { assessmentsApi } from '@/lib/api';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { NewAssessmentDialog } from '@/components/dialogs/NewAssessmentDialog';

export default function AssessmentsPage() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewAssessmentDialog, setShowNewAssessmentDialog] = useState(false);

  const fetchAssessments = async () => {
    try {
      setLoading(true);
      const response = await assessmentsApi.getAll();
      setAssessments(response.items || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch assessments');
      console.error('Error fetching assessments:', err);
      setAssessments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssessments();
  }, []);

  const filteredAssessments = assessments.filter((assessment: any) =>
    assessment.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    assessment.framework?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
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

  const handleNewAssessment = () => {
    console.log('New Assessment clicked - Opening assessment creation dialog');
    setShowNewAssessmentDialog(true);
  };

  const handleAssessmentCreated = () => {
    console.log('Assessment created successfully - refreshing assessments list');
    fetchAssessments();
  };

  const handleSchedule = () => {
    console.log('Schedule clicked - Opening assessment scheduling dialog');
    alert('Schedule functionality would open a scheduling dialog for assessments');
    // TODO: Implement assessment scheduling dialog
  };

  const handleFilters = () => {
    console.log('Filters clicked - Opening filters dialog');
    alert('Filters functionality would open a filters panel for assessments');
    // TODO: Implement filters dialog
  };

  const handleViewDetails = (assessmentId: string) => {
    console.log('View Details clicked for assessment:', assessmentId);
    navigate(`/assessments/${assessmentId}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Security Assessments
          </h1>
          <p className="text-muted-foreground">
            Manage security and compliance assessments across frameworks
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleSchedule}>
            <Calendar className="h-4 w-4 mr-2" />
            Schedule
          </Button>
          <Button onClick={handleNewAssessment}>
            <Plus className="h-4 w-4 mr-2" />
            New Assessment
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search assessments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-sm"
          />
        </div>
        <Button variant="outline" size="sm" onClick={handleFilters}>
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
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
            <CardTitle className="text-sm font-medium">Total Assessments</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{assessments.length}</div>
            <p className="text-xs text-muted-foreground">
              Active assessments
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assessments.filter(a => a.status === 'In Progress').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently active
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assessments.filter(a => a.status === 'Completed').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Successfully finished
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Frameworks</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(assessments.map(a => a.framework)).size}
            </div>
            <p className="text-xs text-muted-foreground">
              Different frameworks
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Assessments List */}
      <Card>
        <CardHeader>
          <CardTitle>Assessments ({filteredAssessments.length})</CardTitle>
          <CardDescription>
            Security and compliance assessments across various frameworks
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredAssessments.length === 0 ? (
            <div className="text-center py-8">
              <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No assessments found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm ? 'Try adjusting your search criteria' : 'Get started by creating your first assessment'}
              </p>
              <Button onClick={handleNewAssessment}>
                <Plus className="h-4 w-4 mr-2" />
                New Assessment
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAssessments.map((assessment: any) => (
                <div
                  key={assessment.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold">{assessment.name}</h3>
                      <Badge variant={getStatusColor(assessment.status)}>
                        {assessment.status || 'Unknown'}
                      </Badge>
                      <Badge variant="outline">
                        {assessment.framework || 'No Framework'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Progress: {assessment.progress || 0}%</span>
                      <span>Due: {assessment.due_date || 'No due date'}</span>
                      <span>Assessor: {assessment.assessor || 'Unassigned'}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" onClick={() => handleViewDetails(assessment.id)}>
                      View Details
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* New Assessment Dialog */}
      <NewAssessmentDialog
        open={showNewAssessmentDialog}
        onOpenChange={setShowNewAssessmentDialog}
        onAssessmentCreated={handleAssessmentCreated}
      />
    </div>
  );
}