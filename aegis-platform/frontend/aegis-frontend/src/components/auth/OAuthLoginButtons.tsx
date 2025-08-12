import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface OAuthProvider {
  name: string;
  display_name: string;
  enabled: boolean;
  icon: string;
}

interface OAuthLoginButtonsProps {
  onOAuthStart?: () => void;
  onOAuthComplete?: (tokens: any) => void;
  onError?: (error: string) => void;
}

const OAuthLoginButtons: React.FC<OAuthLoginButtonsProps> = ({
  onOAuthStart,
  onOAuthComplete,
  onError
}) => {
  const [providers, setProviders] = useState<OAuthProvider[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingProvider, setLoadingProvider] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOAuthProviders();
    
    // Handle OAuth callback if we're on the callback page
    handleOAuthCallback();
  }, []);

  const fetchOAuthProviders = async () => {
    try {
      const response = await fetch('/api/v1/oauth/providers');
      if (response.ok) {
        const data = await response.json();
        setProviders(data.providers.filter((p: OAuthProvider) => p.enabled));
      }
    } catch (err) {
      console.error('Failed to fetch OAuth providers:', err);
    }
  };

  const handleOAuthCallback = () => {
    // Check if we're on an OAuth callback URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const error = urlParams.get('error');
    
    if (error) {
      setError(`OAuth authentication failed: ${error}`);
      onError?.(error);
      return;
    }
    
    if (code && state) {
      // Extract provider from current path or state
      const pathParts = window.location.pathname.split('/');
      const provider = pathParts[pathParts.indexOf('callback') + 1];
      
      if (provider) {
        completeOAuthFlow(provider, code, state);
      }
    }
  };

  const startOAuthFlow = async (provider: string) => {
    try {
      setLoadingProvider(provider);
      setError(null);
      onOAuthStart?.();

      const response = await fetch(`/api/v1/oauth/authorize/${provider}?redirect_url=${encodeURIComponent(window.location.origin + '/dashboard')}`);
      
      if (!response.ok) {
        throw new Error('Failed to initiate OAuth flow');
      }

      const data = await response.json();
      
      // Redirect to OAuth provider
      window.location.href = data.authorization_url;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'OAuth flow failed';
      setError(errorMessage);
      onError?.(errorMessage);
      setLoadingProvider(null);
    }
  };

  const completeOAuthFlow = async (provider: string, code: string, state: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/v1/oauth/callback/${provider}?code=${code}&state=${state}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'OAuth callback failed');
      }

      const tokens = await response.json();
      
      // Store tokens (in production, consider using HTTP-only cookies)
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      localStorage.setItem('user', JSON.stringify(tokens.user));
      
      onOAuthComplete?.(tokens);
      
      // Redirect to specified URL or dashboard
      window.location.href = tokens.redirect_url || '/dashboard';
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'OAuth completion failed';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getProviderIcon = (iconName: string) => {
    const iconMap: { [key: string]: JSX.Element } = {
      microsoft: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zM24 11.4H12.6V0H24v11.4z" fill="#00BCF2"/>
        </svg>
      ),
      google: (
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
      ),
      okta: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="#007DC1"/>
          <circle cx="12" cy="12" r="4" fill="#007DC1"/>
        </svg>
      )
    };
    
    return iconMap[iconName] || <AlertCircle className="w-5 h-5" />;
  };

  if (providers.length === 0) {
    return null; // Don't show OAuth section if no providers are enabled
  }

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground text-center">
          Sign in with your enterprise account
        </p>
        
        {providers.map((provider) => (
          <Button
            key={provider.name}
            variant="outline"
            className="w-full"
            onClick={() => startOAuthFlow(provider.name)}
            disabled={loading || loadingProvider !== null}
          >
            {loadingProvider === provider.name ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <span className="mr-2">{getProviderIcon(provider.icon)}</span>
            )}
            Continue with {provider.display_name}
          </Button>
        ))}
      </div>
      
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <Separator className="w-full" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with email
          </span>
        </div>
      </div>
    </div>
  );
};

export default OAuthLoginButtons;