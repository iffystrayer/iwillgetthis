import { useState, useEffect } from 'react';
import { Plus, FileText, Filter, Upload, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { evidenceApi } from '@/lib/api';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { UploadEvidenceDialog } from '@/components/dialogs/UploadEvidenceDialog';

export default function EvidencePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [evidence, setEvidence] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUploadDialog, setShowUploadDialog] = useState(false);

  const fetchEvidence = async () => {
    try {
      setLoading(true);
      const response = await evidenceApi.getAll();
      setEvidence(response.items || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch evidence');
      console.error('Error fetching evidence:', err);
      setEvidence([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, []);

  const filteredEvidence = evidence.filter((item: any) =>
    item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.description?.toLowerCase().includes(searchTerm.toLowerCase())
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
      case 'approved': return 'default';
      case 'under review': return 'secondary';
      case 'pending': return 'outline';
      case 'rejected': return 'destructive';
      default: return 'outline';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'policy': return 'default';
      case 'technical': return 'secondary';
      case 'training': return 'outline';
      case 'administrative': return 'secondary';
      default: return 'outline';
    }
  };

  const handleUploadEvidence = () => {
    console.log('Upload Evidence clicked - Opening file upload dialog');
    setShowUploadDialog(true);
  };

  const handleEvidenceUploaded = () => {
    console.log('Evidence uploaded successfully - refreshing evidence list');
    fetchEvidence();
  };

  const handleExportAll = () => {
    console.log('Export All clicked - Exporting all evidence files');
    console.log('Export All functionality would download all evidence files as a ZIP archive');
    // TODO: Implement bulk export functionality
  };

  const handleFilters = () => {
    console.log('Filters clicked - Opening filters dialog');
    console.log('Filters functionality would open a filters panel for evidence');
    // TODO: Implement filters dialog
  };

  const handleDownload = async (evidenceId: string) => {
    console.log('Download clicked for evidence:', evidenceId);
    try {
      const response = await evidenceApi.download(evidenceId);
      
      // Create a blob from the response data
      const blob = new Blob([response.data], { 
        type: response.headers['content-type'] || 'application/octet-stream' 
      });
      
      // Get filename from response headers or use a default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `evidence-${evidenceId}`;
      if (contentDisposition && contentDisposition.includes('filename=')) {
        filename = contentDisposition
          .split('filename=')[1]
          .replace(/['"]/g, '');
      }
      
      // Create download link and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log(`Evidence ${evidenceId} downloaded successfully`);
    } catch (error: any) {
      console.error('Error downloading evidence:', error);
      console.log(`Failed to download evidence: ${error.message || 'Unknown error'}`);
    }
  };

  const handleViewDetails = (evidenceId: string) => {
    console.log('View Details clicked for evidence:', evidenceId);
    console.log(`View Details functionality would show detailed view for evidence ${evidenceId}`);
    // TODO: Navigate to evidence details page or open details modal
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <FileText className="h-8 w-8" />
            Evidence Management
          </h1>
          <p className="text-muted-foreground">
            Manage compliance evidence and supporting documentation
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleExportAll}>
            <Download className="h-4 w-4 mr-2" />
            Export All
          </Button>
          <Button onClick={handleUploadEvidence}>
            <Upload className="h-4 w-4 mr-2" />
            Upload Evidence
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search evidence..."
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
              Showing demo data while backend is unavailable.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Evidence</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{evidence.length}</div>
            <p className="text-xs text-muted-foreground">
              Files in repository
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {evidence.filter(e => e.status === 'Approved').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Ready for audit
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Under Review</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {evidence.filter(e => e.status === 'Under Review').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Pending approval
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Evidence Types</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(evidence.map(e => e.type)).size}
            </div>
            <p className="text-xs text-muted-foreground">
              Different categories
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Evidence List */}
      <Card>
        <CardHeader>
          <CardTitle>Evidence ({filteredEvidence.length})</CardTitle>
          <CardDescription>
            Compliance evidence and supporting documentation
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredEvidence.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No evidence found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm ? 'Try adjusting your search criteria' : 'Get started by uploading your first evidence file'}
              </p>
              <Button onClick={handleUploadEvidence}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Evidence
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredEvidence.map((item: any) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold">{item.title}</h3>
                      <Badge variant={getStatusColor(item.status)}>
                        {item.status || 'Unknown'}
                      </Badge>
                      <Badge variant={getTypeColor(item.type)}>
                        {item.type || 'Unknown'}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">
                      {item.description || 'No description available'}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Size: {item.size || 'Unknown'}</span>
                      {item.uploaded && (
                        <span>Uploaded: {new Date(item.uploaded).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" onClick={() => handleDownload(item.id)}>
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleViewDetails(item.id)}>
                      View Details
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Evidence Dialog */}
      <UploadEvidenceDialog
        open={showUploadDialog}
        onOpenChange={setShowUploadDialog}
        onEvidenceUploaded={handleEvidenceUploaded}
      />
    </div>
  );
}