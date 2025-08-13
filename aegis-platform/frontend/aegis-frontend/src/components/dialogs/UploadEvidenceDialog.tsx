import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Upload, X, FileText, AlertCircle } from 'lucide-react';
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
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { evidenceApi } from '@/lib/api';

interface UploadEvidenceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onEvidenceUploaded?: () => void;
}

interface EvidenceFormData {
  title: string;
  description: string;
  type: string;
  file: FileList | null;
}

const evidenceTypes = [
  { value: 'document', label: 'Document' },
  { value: 'policy', label: 'Policy' },
  { value: 'technical', label: 'Technical' },
  { value: 'training', label: 'Training' },
  { value: 'administrative', label: 'Administrative' },
  { value: 'procedure', label: 'Procedure' },
  { value: 'certificate', label: 'Certificate' },
  { value: 'report', label: 'Report' },
  { value: 'other', label: 'Other' }
];

export function UploadEvidenceDialog({ open, onOpenChange, onEvidenceUploaded }: UploadEvidenceDialogProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { register, handleSubmit, reset, setValue, formState: { errors }, watch } = useForm<EvidenceFormData>();

  const selectedType = watch('type');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      // Auto-generate title from filename if not already set
      if (!watch('title')) {
        const titleFromFile = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
        setValue('title', titleFromFile);
      }
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFileType = (file: File): boolean => {
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/plain',
      'text/csv',
      'image/jpeg',
      'image/png',
      'image/gif'
    ];
    return allowedTypes.includes(file.type);
  };

  const onSubmit = async (data: EvidenceFormData) => {
    if (!selectedFile) {
      setUploadError('Please select a file to upload');
      return;
    }

    if (!validateFileType(selectedFile)) {
      setUploadError('Invalid file type. Please upload PDF, Word, Excel, text, or image files only.');
      return;
    }

    // Check file size (max 50MB)
    if (selectedFile.size > 50 * 1024 * 1024) {
      setUploadError('File size must be less than 50MB');
      return;
    }

    try {
      setIsUploading(true);
      setUploadError(null);

      const formData = new FormData();
      formData.append('file', selectedFile);

      // Use the corrected evidence API with proper parameters
      await evidenceApi.upload(formData, data.title, data.type, data.description);

      // Reset form and close dialog
      reset();
      setSelectedFile(null);
      onOpenChange(false);
      
      // Notify parent component
      if (onEvidenceUploaded) {
        onEvidenceUploaded();
      }

      console.log('✅ Evidence uploaded successfully');
    } catch (error: any) {
      console.error('❌ Error uploading evidence:', error);
      setUploadError(error.response?.data?.detail || error.message || 'Failed to upload evidence. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    if (!isUploading) {
      reset();
      setSelectedFile(null);
      setUploadError(null);
      onOpenChange(false);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setUploadError(null);
    // Reset file input
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md form-glass border-0">
        <DialogHeader className="text-center space-y-3">
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            ✨ Upload Evidence
          </DialogTitle>
          <DialogDescription className="text-muted-foreground/80">
            Upload compliance evidence and supporting documentation with our secure platform
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* File Upload - Glassmorphism */}
          <div className="space-y-3">
            <Label htmlFor="file" className="text-sm font-semibold text-foreground/90">📁 File</Label>
            <div className="glass border-2 border-dashed border-primary/30 rounded-xl p-8 text-center hover:border-primary/50 transition-all duration-300">
              {selectedFile ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <FileText className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="font-medium">{selectedFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={removeFile}
                    className="mt-2"
                  >
                    <X className="h-4 w-4 mr-2" />
                    Remove
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="h-8 w-8 text-muted-foreground mx-auto" />
                  <div>
                    <p className="font-medium">Click to upload or drag and drop</p>
                    <p className="text-sm text-muted-foreground">
                      PDF, Word, Excel, Text, or Image files (max 50MB)
                    </p>
                  </div>
                  <Input
                    id="file"
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.csv,.jpg,.jpeg,.png,.gif"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Title - Glass Input */}
          <div className="space-y-3">
            <Label htmlFor="title" className="text-sm font-semibold text-foreground/90">✨ Title *</Label>
            <Input
              id="title"
              {...register('title', { required: 'Title is required' })}
              placeholder="Enter evidence title"
              className="input-glass h-12 text-base"
            />
            {errors.title && (
              <p className="text-sm text-red-500 font-medium">{errors.title.message}</p>
            )}
          </div>

          {/* Description - Glass Textarea */}
          <div className="space-y-3">
            <Label htmlFor="description" className="text-sm font-semibold text-foreground/90">📝 Description</Label>
            <Textarea
              id="description"
              {...register('description')}
              placeholder="Describe the evidence (optional)"
              rows={3}
              className="input-glass resize-none"
            />
          </div>

          {/* Type - Glass Select */}
          <div className="space-y-3">
            <Label htmlFor="type" className="text-sm font-semibold text-foreground/90">🏷️ Type *</Label>
            <Select
              value={selectedType}
              onValueChange={(value) => setValue('type', value)}
            >
              <SelectTrigger className="input-glass h-12">
                <SelectValue placeholder="Select evidence type" />
              </SelectTrigger>
              <SelectContent className="glass border-0">
                {evidenceTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value} className="hover:bg-primary/10">
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.type && (
              <p className="text-sm text-red-500 font-medium">Evidence type is required</p>
            )}
          </div>

          {/* Error Alert - Glass Style */}
          {uploadError && (
            <Alert variant="destructive" className="glass border-red-200/50 bg-red-50/80">
              <AlertCircle className="h-5 w-5" />
              <AlertDescription className="font-medium">{uploadError}</AlertDescription>
            </Alert>
          )}

          {/* Actions - Gradient Buttons */}
          <div className="flex justify-end space-x-3 pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isUploading}
              className="glass border-primary/20 hover:border-primary/40 px-6 h-11"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isUploading || !selectedFile}
              className="btn-gradient-primary px-8 h-11 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Evidence
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}