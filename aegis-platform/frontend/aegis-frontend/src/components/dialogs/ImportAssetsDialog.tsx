import { useState } from 'react';
import { Upload, X, FileText, AlertCircle, Download, Info } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { assetsApi } from '@/lib/api';

interface ImportAssetsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAssetsImported?: () => void;
}

export function ImportAssetsDialog({ open, onOpenChange, onAssetsImported }: ImportAssetsDialogProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['.csv', '.xlsx', '.xls'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!allowedTypes.includes(fileExtension)) {
        setError(`Invalid file type. Please select a CSV or Excel file (${allowedTypes.join(', ')})`);
        return;
      }
      
      // Validate file size (10MB limit)
      const maxSize = 10 * 1024 * 1024; // 10MB in bytes
      if (file.size > maxSize) {
        setError('File size must be less than 10MB. Please select a smaller file.');
        return;
      }
      
      // Validate file is not empty
      if (file.size === 0) {
        setError('File appears to be empty. Please select a file with data.');
        return;
      }
      
      setSelectedFile(file);
      setError(null);
      setSuccess(null);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError(null);
    setSuccess(null);
  };

  const handleUpload = async () => {
    // Validation checks
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    // Double-check file type before upload
    const allowedTypes = ['.csv', '.xlsx', '.xls'];
    const fileExtension = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
    if (!allowedTypes.includes(fileExtension)) {
      setError('Invalid file type. Only CSV and Excel files are supported.');
      return;
    }

    // Double-check file size before upload
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (selectedFile.size > maxSize) {
      setError('File size exceeds 10MB limit.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      console.log('Uploading asset file:', selectedFile.name);
      
      // Upload file using the assets API
      const response = await assetsApi.import(selectedFile);
      
      console.log('✅ Assets imported successfully:', response);
      
      setSuccess(`Successfully imported ${response.success_count || 0} assets from ${selectedFile.name}. ${response.error_count > 0 ? `${response.error_count} errors occurred.` : ''}`);
      
      if (onAssetsImported) {
        onAssetsImported();
      }
      
      // Reset form after successful upload
      setTimeout(() => {
        handleClose();
      }, 1500);
      
    } catch (err: any) {
      console.error('❌ Failed to import assets:', err);
      setError(err.message || 'Failed to import assets. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setError(null);
    setSuccess(null);
    onOpenChange(false);
  };

  const downloadTemplate = () => {
    // Create a sample CSV template
    const csvContent = `name,description,category,criticality,status,owner
"Web Server","Main application server","Infrastructure","Critical","Active","IT Team"
"Database Server","Primary database","Infrastructure","Critical","Active","IT Team"
"Laptop - John Doe","Employee workstation","Endpoint","Medium","Active","John Doe"
"Mobile App","Customer mobile application","Application","High","Active","Dev Team"`;
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'assets_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] form-glass border-0">
        <DialogHeader className="text-center space-y-3">
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center justify-center gap-3">
            <Upload className="h-6 w-6 text-indigo-600" />
            📥 Import Assets
          </DialogTitle>
          <DialogDescription className="text-muted-foreground/80">
            Upload a CSV or Excel file to bulk import assets into your inventory
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Template Download Section */}
          <Card className="glass border-blue-200/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Download className="h-5 w-5" />
                📋 Download Template
              </CardTitle>
              <CardDescription>
                Download a sample CSV template with the correct format and example data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={downloadTemplate}
                variant="outline" 
                className="w-full glass border-blue-300/50 hover:border-blue-400/50"
              >
                <Download className="h-4 w-4 mr-2" />
                Download CSV Template
              </Button>
            </CardContent>
          </Card>

          {/* File Upload Section */}
          <div className="space-y-4">
            <Label className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
              <FileText className="h-4 w-4" />
              📎 Select File
            </Label>
            
            {!selectedFile ? (
              <div className="border-2 border-dashed border-primary/20 rounded-xl p-8 text-center glass hover:border-primary/40 transition-colors">
                <Upload className="h-12 w-12 mx-auto mb-4 text-primary/60" />
                <div className="space-y-2">
                  <p className="text-sm font-medium">
                    Choose a file to upload
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Supports CSV, Excel (.xlsx, .xls) files up to 10MB
                  </p>
                </div>
                <Input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  className="mt-4"
                />
              </div>
            ) : (
              <div className="glass rounded-xl p-4 border border-green-200/50 bg-green-50/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8 text-green-600" />
                    <div>
                      <p className="font-medium text-green-800">{selectedFile.name}</p>
                      <p className="text-sm text-green-600">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Button
                    onClick={handleRemoveFile}
                    variant="ghost"
                    size="sm"
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Format Requirements */}
          <Alert className="glass border-blue-200/50 bg-blue-50/20">
            <Info className="h-4 w-4" />
            <AlertDescription className="text-sm">
              <strong>Required columns:</strong> name, description, category, criticality, status, owner<br/>
              <strong>Optional columns:</strong> location, purchase_date, value, vendor
            </AlertDescription>
          </Alert>

          {/* Success Message */}
          {success && (
            <Alert className="glass border-green-200/50 bg-green-50/20">
              <AlertCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800 font-medium">
                {success}
              </AlertDescription>
            </Alert>
          )}

          {/* Error Message */}
          {error && (
            <Alert className="glass border-red-200/50 bg-red-50/20">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800 font-medium">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4">
            <Button
              onClick={handleClose}
              variant="outline"
              disabled={isUploading}
              className="glass border-primary/20 hover:border-primary/40 px-6"
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className="btn-gradient-primary px-8 text-white font-semibold disabled:opacity-50"
            >
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Importing...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Import Assets
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}