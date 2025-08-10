import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  showDetails?: boolean;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorDisplay 
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          showDetails={this.props.showDetails}
          onRetry={() => this.setState({ hasError: false, error: undefined, errorInfo: undefined })}
        />
      );
    }

    return this.props.children;
  }
}

// Error display component
interface ErrorDisplayProps {
  error?: Error;
  errorInfo?: ErrorInfo;
  showDetails?: boolean;
  onRetry?: () => void;
  title?: string;
  description?: string;
}

export function ErrorDisplay({ 
  error, 
  errorInfo, 
  showDetails = false, 
  onRetry, 
  title = "Something went wrong",
  description = "An unexpected error occurred while loading this section."
}: ErrorDisplayProps) {
  const [showErrorDetails, setShowErrorDetails] = React.useState(false);

  return (
    <Card className="border-destructive">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="rounded-full bg-destructive/10 p-3">
            <AlertTriangle className="h-6 w-6 text-destructive" />
          </div>
        </div>
        <CardTitle className="text-destructive">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex justify-center gap-2">
          {onRetry && (
            <Button onClick={onRetry} size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={() => window.location.href = '/'}>
            <Home className="h-4 w-4 mr-2" />
            Go Home
          </Button>
        </div>

        {(showDetails && error) && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className="text-xs">
                <Bug className="h-3 w-3 mr-1" />
                Debug Info
              </Badge>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setShowErrorDetails(!showErrorDetails)}
              >
                {showErrorDetails ? 'Hide' : 'Show'} Details
              </Button>
            </div>
            
            {showErrorDetails && (
              <div className="bg-muted p-3 rounded-md text-sm font-mono space-y-2">
                <div>
                  <strong>Error:</strong> {error.message}
                </div>
                {error.stack && (
                  <div>
                    <strong>Stack Trace:</strong>
                    <pre className="text-xs mt-1 whitespace-pre-wrap">{error.stack}</pre>
                  </div>
                )}
                {errorInfo && (
                  <div>
                    <strong>Component Stack:</strong>
                    <pre className="text-xs mt-1 whitespace-pre-wrap">{errorInfo.componentStack}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Network error component
export function NetworkError({ 
  onRetry, 
  message = "Unable to connect to the server" 
}: { 
  onRetry?: () => void; 
  message?: string; 
}) {
  return (
    <ErrorDisplay
      title="Connection Error"
      description={message}
      onRetry={onRetry}
    />
  );
}

// API error component
export function ApiError({ 
  status, 
  message, 
  onRetry 
}: { 
  status?: number; 
  message?: string; 
  onRetry?: () => void; 
}) {
  const getStatusMessage = (status?: number) => {
    switch (status) {
      case 400: return "Bad Request - The request was invalid";
      case 401: return "Unauthorized - Please log in again";
      case 403: return "Forbidden - You don't have permission to access this resource";
      case 404: return "Not Found - The requested resource could not be found";
      case 500: return "Internal Server Error - Something went wrong on our end";
      case 502: return "Bad Gateway - The server is temporarily unavailable";
      case 503: return "Service Unavailable - The service is temporarily down";
      default: return message || "An error occurred while communicating with the server";
    }
  };

  return (
    <ErrorDisplay
      title={status ? `Error ${status}` : "API Error"}
      description={getStatusMessage(status)}
      onRetry={onRetry}
    />
  );
}

// Form error component
export function FormError({ 
  errors, 
  title = "Validation Error" 
}: { 
  errors: string[] | Record<string, string[]>; 
  title?: string; 
}) {
  const errorList = Array.isArray(errors) 
    ? errors 
    : Object.entries(errors).flatMap(([field, fieldErrors]) => 
        fieldErrors.map(error => `${field}: ${error}`)
      );

  return (
    <Card className="border-destructive bg-destructive/5">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm text-destructive flex items-center gap-2">
          <AlertTriangle className="h-4 w-4" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <ul className="space-y-1 text-sm text-destructive">
          {errorList.map((error, index) => (
            <li key={index} className="flex items-start gap-2">
              <span className="text-destructive/60">•</span>
              {error}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}