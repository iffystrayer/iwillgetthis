import { useState, useEffect } from 'react';
import { Plus, X, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { integrationsApi } from '@/lib/api';
import { useNotifications } from '@/hooks/useNotifications';

interface IntegrationType {
  id: string;
  name: string;
  category: string;
  display_name: string;
  description: string;
  capabilities: string[];
  auth_methods: string[];
  default_port: number;
  requires_ssl: boolean;
  is_enterprise: boolean;
}

interface CreateIntegrationDialogProps {
  onSuccess?: () => void;
}

export default function CreateIntegrationDialog({ onSuccess }: CreateIntegrationDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [integrationTypes, setIntegrationTypes] = useState<IntegrationType[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedType, setSelectedType] = useState<IntegrationType | null>(null);
  const [testResult, setTestResult] = useState<any>(null);
  
  const { addNotification } = useNotifications();
  
  const [formData, setFormData] = useState({
    name: '',
    integration_type: '',
    endpoint_url: '',
    username: '',
    password: '',
    api_key: '',
    auth_method: 'basic',
    description: '',
    configuration: {} as Record<string, any>
  });

  useEffect(() => {
    if (isOpen) {
      fetchIntegrationTypes();
    }
  }, [isOpen]);

  const fetchIntegrationTypes = async () => {
    try {
      const response = await integrationsApi.getTypes();
      setIntegrationTypes(response);
    } catch (error) {
      console.error('Failed to fetch integration types:', error);
      addNotification({
        type: 'error',
        title: 'Integration Types',
        message: 'Failed to load integration types',
        priority: 'medium',
        category: 'system'
      });
    }
  };

  const categories = [...new Set(integrationTypes.map(type => type.category))];
  const filteredTypes = selectedCategory 
    ? integrationTypes.filter(type => type.category === selectedCategory)
    : integrationTypes;

  const handleTypeSelect = (typeId: string) => {
    const type = integrationTypes.find(t => t.id === typeId);
    if (type) {
      setSelectedType(type);
      setFormData(prev => ({
        ...prev,
        integration_type: type.name,
        auth_method: type.auth_methods[0] || 'basic',
        endpoint_url: type.requires_ssl ? 'https://' : 'http://',
        configuration: {
          default_port: type.default_port,
          requires_ssl: type.requires_ssl
        }
      }));
      setTestResult(null);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setTestResult(null);
  };

  const handleConfigChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      configuration: {
        ...prev.configuration,
        [field]: value
      }
    }));
  };

  const handleTestConnection = async () => {
    if (!selectedType || !formData.name || !formData.endpoint_url) {
      addNotification({
        type: 'error',
        title: 'Validation Error',
        message: 'Please fill in required fields before testing',
        priority: 'medium',
        category: 'validation'
      });
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      // First create the connector
      const createResponse = await integrationsApi.createConnector(formData);
      
      if (createResponse.success) {
        const connectorId = createResponse.connector_id;
        
        // Then test the connection
        const testResponse = await integrationsApi.testConnector(String(connectorId));
        setTestResult(testResponse);
        
        if (testResponse.success) {
          addNotification({
            type: 'success',
            title: 'Connection Test',
            message: 'Connection test successful!',
            priority: 'medium',
            category: 'integration'
          });
        } else {
          addNotification({
            type: 'error',
            title: 'Connection Test',
            message: `Connection test failed: ${testResponse.message || testResponse.error}`,
            priority: 'high',
            category: 'integration'
          });
        }
      } else {
        setTestResult({ success: false, message: 'Failed to create connector' });
        addNotification({
          type: 'error',
          title: 'Connector Creation',
          message: 'Failed to create connector for testing',
          priority: 'high',
          category: 'integration'
        });
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Connection test failed';
      setTestResult({ success: false, message: errorMessage });
      addNotification({
        type: 'error',
        title: 'Connection Test',
        message: `Connection test failed: ${errorMessage}`,
        priority: 'high',
        category: 'integration'
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedType || !formData.name || !formData.endpoint_url) {
      addNotification({
        type: 'error',
        title: 'Validation Error',
        message: 'Please fill in all required fields',
        priority: 'medium',
        category: 'validation'
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await integrationsApi.createConnector(formData);
      
      if (response.success) {
        addNotification({
          type: 'success',
          title: 'Integration Created',
          message: `Integration "${formData.name}" created successfully!`,
          priority: 'medium',
          category: 'integration'
        });
        setIsOpen(false);
        resetForm();
        onSuccess?.();
      } else {
        addNotification({
          type: 'error',
          title: 'Integration Creation',
          message: 'Failed to create integration',
          priority: 'high',
          category: 'integration'
        });
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create integration';
      addNotification({
        type: 'error',
        title: 'Integration Creation',
        message: errorMessage,
        priority: 'high',
        category: 'integration'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      integration_type: '',
      endpoint_url: '',
      username: '',
      password: '',
      api_key: '',
      auth_method: 'basic',
      description: '',
      configuration: {}
    });
    setSelectedCategory('');
    setSelectedType(null);
    setTestResult(null);
  };

  const renderAuthFields = () => {
    if (!selectedType) return null;

    return (
      <div className="space-y-4">
        <div>
          <Label htmlFor="auth_method">Authentication Method</Label>
          <Select value={formData.auth_method} onValueChange={(value) => handleInputChange('auth_method', value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {selectedType.auth_methods.map((method) => (
                <SelectItem key={method} value={method}>
                  {method.charAt(0).toUpperCase() + method.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {(formData.auth_method === 'basic') && (
          <>
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                placeholder="Enter username"
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                placeholder="Enter password"
              />
            </div>
          </>
        )}

        {(formData.auth_method === 'token' || formData.auth_method === 'api_key') && (
          <div>
            <Label htmlFor="api_key">API Key/Token</Label>
            <Input
              id="api_key"
              type="password"
              value={formData.api_key}
              onChange={(e) => handleInputChange('api_key', e.target.value)}
              placeholder="Enter API key or token"
            />
          </div>
        )}

        {formData.auth_method === 'oauth' && (
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-700">
              OAuth authentication requires additional configuration. Please refer to the documentation for your specific platform.
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderConfigFields = () => {
    if (!selectedType) return null;

    const specificFields = getSpecificConfigFields(selectedType);
    
    return (
      <div className="space-y-4">
        {specificFields.map((field) => (
          <div key={field.name}>
            <Label htmlFor={field.name}>{field.label}</Label>
            {field.type === 'text' ? (
              <Input
                id={field.name}
                value={formData.configuration[field.name] || ''}
                onChange={(e) => handleConfigChange(field.name, e.target.value)}
                placeholder={field.placeholder}
              />
            ) : field.type === 'number' ? (
              <Input
                id={field.name}
                type="number"
                value={formData.configuration[field.name] || ''}
                onChange={(e) => handleConfigChange(field.name, parseInt(e.target.value))}
                placeholder={field.placeholder}
              />
            ) : field.type === 'select' ? (
              <Select 
                value={formData.configuration[field.name] || ''} 
                onValueChange={(value) => handleConfigChange(field.name, value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder={field.placeholder} />
                </SelectTrigger>
                <SelectContent>
                  {field.options?.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : null}
            {field.description && (
              <p className="text-sm text-muted-foreground mt-1">{field.description}</p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const getSpecificConfigFields = (type: IntegrationType) => {
    const commonFields = [];

    switch (type.name) {
      case 'splunk':
        return [
          { name: 'app', label: 'Splunk App', type: 'text', placeholder: 'search', description: 'Splunk app context' },
          { name: 'owner', label: 'Owner', type: 'text', placeholder: 'admin', description: 'Splunk user context' }
        ];
      
      case 'sentinel':
        return [
          { name: 'subscription_id', label: 'Subscription ID', type: 'text', placeholder: 'Azure subscription ID' },
          { name: 'resource_group', label: 'Resource Group', type: 'text', placeholder: 'Azure resource group name' },
          { name: 'workspace_name', label: 'Workspace Name', type: 'text', placeholder: 'Log Analytics workspace name' },
          { name: 'tenant_id', label: 'Tenant ID', type: 'text', placeholder: 'Azure AD tenant ID' },
          { name: 'client_id', label: 'Client ID', type: 'text', placeholder: 'Azure app registration client ID' }
        ];
      
      case 'elastic':
        return [
          { name: 'default_index', label: 'Default Index', type: 'text', placeholder: 'logs-*', description: 'Default Elasticsearch index pattern' },
          { name: 'security_index', label: 'Security Index', type: 'text', placeholder: 'winlogbeat-*,filebeat-*', description: 'Security-specific index patterns' }
        ];
      
      case 'servicenow':
        return [
          { name: 'controls_table', label: 'Controls Table', type: 'text', placeholder: 'grc_control', description: 'ServiceNow table for GRC controls' },
          { name: 'incidents_table', label: 'Incidents Table', type: 'text', placeholder: 'incident', description: 'ServiceNow table for incidents' }
        ];
      
      case 'archer':
        return [
          { name: 'instance_name', label: 'Instance Name', type: 'text', placeholder: 'default', description: 'Archer instance name' },
          { name: 'domain', label: 'Domain', type: 'text', placeholder: '', description: 'User domain (optional)' },
          { name: 'controls_app_id', label: 'Controls App ID', type: 'number', placeholder: '75', description: 'Archer application ID for controls' }
        ];
      
      default:
        return commonFields;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button onClick={() => setIsOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Integration
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Integration</DialogTitle>
          <DialogDescription>
            Connect to enterprise SIEM and GRC platforms to centralize your security data.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Integration Type Selection */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="category">Category</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="Select integration category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category.toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredTypes.map((type) => (
                <Card 
                  key={type.id} 
                  className={`cursor-pointer transition-colors ${
                    selectedType?.id === type.id ? 'ring-2 ring-primary' : 'hover:bg-muted/50'
                  }`}
                  onClick={() => handleTypeSelect(type.id)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm">{type.display_name}</CardTitle>
                      <div className="flex gap-1">
                        <Badge variant={type.category === 'siem' ? 'default' : 'secondary'}>
                          {type.category.toUpperCase()}
                        </Badge>
                        {type.is_enterprise && (
                          <Badge variant="outline">Enterprise</Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-xs">{type.description}</CardDescription>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {type.capabilities.slice(0, 3).map((cap) => (
                        <Badge key={cap} variant="outline" className="text-xs">
                          {cap.replace('_', ' ')}
                        </Badge>
                      ))}
                      {type.capabilities.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{type.capabilities.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Configuration Form */}
          {selectedType && (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Basic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Integration Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      placeholder={`My ${selectedType.display_name}`}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="endpoint_url">Endpoint URL *</Label>
                    <Input
                      id="endpoint_url"
                      value={formData.endpoint_url}
                      onChange={(e) => handleInputChange('endpoint_url', e.target.value)}
                      placeholder={`${selectedType.requires_ssl ? 'https' : 'http'}://your-server:${selectedType.default_port}`}
                      required
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="Optional description for this integration"
                    rows={2}
                  />
                </div>
              </div>

              {/* Authentication */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Authentication</h3>
                {renderAuthFields()}
              </div>

              {/* Platform-specific Configuration */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Configuration</h3>
                {renderConfigFields()}
              </div>

              {/* Connection Test Result */}
              {testResult && (
                <div className={`p-4 rounded-lg ${
                  testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center gap-2">
                    {testResult.success ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    )}
                    <span className={`font-medium ${
                      testResult.success ? 'text-green-700' : 'text-red-700'
                    }`}>
                      {testResult.success ? 'Connection Successful' : 'Connection Failed'}
                    </span>
                  </div>
                  <p className={`text-sm mt-1 ${
                    testResult.success ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {testResult.message || testResult.error}
                  </p>
                  {testResult.details && (
                    <div className="mt-2 text-xs text-muted-foreground">
                      <pre className="whitespace-pre-wrap">{JSON.stringify(testResult.details, null, 2)}</pre>
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 justify-end">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsOpen(false)}
                  disabled={isLoading || isTesting}
                >
                  Cancel
                </Button>
                <Button 
                  type="button" 
                  variant="secondary" 
                  onClick={handleTestConnection}
                  disabled={isLoading || isTesting || !formData.name || !formData.endpoint_url}
                >
                  {isTesting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Test Connection
                </Button>
                <Button 
                  type="submit" 
                  disabled={isLoading || isTesting}
                >
                  {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Create Integration
                </Button>
              </div>
            </form>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}