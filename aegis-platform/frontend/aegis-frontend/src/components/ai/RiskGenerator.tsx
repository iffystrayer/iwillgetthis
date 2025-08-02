import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Loader2, AlertTriangle, Brain, Target, TrendingUp } from 'lucide-react';
import ProviderSelector from './ProviderSelector';
import { aiApi } from '../../lib/api';
import { RiskGenerationResponse, RemediationResponse } from '../../types/ai';

interface RiskGeneratorProps {
  assetId?: string;
  controlId?: string;
  vulnerabilityData?: any;
  threatIntelData?: any;
  onRiskGenerated?: (risk: any) => void;
  className?: string;
}

const RiskGenerator: React.FC<RiskGeneratorProps> = ({
  assetId,
  controlId,
  vulnerabilityData,
  threatIntelData,
  onRiskGenerated,
  className = ''
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedRisk, setGeneratedRisk] = useState<RiskGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string | undefined>(undefined);
  const [customContext, setCustomContext] = useState('');
  const [riskType, setRiskType] = useState('technical');
  const [businessImpact, setBusinessImpact] = useState('');

  const generateRisk = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      
      const response = await aiApi.generateRisk({
        asset_id: assetId,
        control_id: controlId,
        vulnerability_data: vulnerabilityData,
        threat_intel_data: threatIntelData,
        custom_context: customContext,
        risk_type: riskType,
        business_impact_context: businessImpact,
        preferred_provider: selectedProvider
      });
      
      setGeneratedRisk(response as RiskGenerationResponse);
      onRiskGenerated?.(response as RiskGenerationResponse);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate risk statement');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateRemediation = async () => {
    if (!generatedRisk) {
      setError('No risk available to generate remediation for');
      return;
    }

    try {
      setIsGenerating(true);
      setError(null);
      
      const response = await aiApi.generateRemediation({
        risk_statement: generatedRisk.risk_statement,
        risk_score: generatedRisk.risk_score,
        asset_context: generatedRisk.asset_context,
        preferred_provider: selectedProvider
      });
      
      setGeneratedRisk(prev => ({
        ...prev!,
        remediation_plan: (response as RemediationResponse).remediation_plan,
        remediation_provider: (response as RemediationResponse).provider_used
      }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate remediation plan');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Provider Selection */}
      <ProviderSelector
        taskType="risk_analysis"
        selectedProvider={selectedProvider}
        onProviderChange={setSelectedProvider}
      />
      
      {/* Risk Generation Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <span>Risk Generation Settings</span>
          </CardTitle>
          <CardDescription>
            Configure the parameters for AI-powered risk statement generation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Risk Type</label>
              <Select value={riskType} onValueChange={setRiskType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technical">Technical Risk</SelectItem>
                  <SelectItem value="operational">Operational Risk</SelectItem>
                  <SelectItem value="compliance">Compliance Risk</SelectItem>
                  <SelectItem value="strategic">Strategic Risk</SelectItem>
                  <SelectItem value="financial">Financial Risk</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Business Impact Context</label>
              <Input
                placeholder="e.g., customer data, financial systems"
                value={businessImpact}
                onChange={(e) => setBusinessImpact(e.target.value)}
              />
            </div>
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Additional Context</label>
            <Textarea
              placeholder="Provide any additional context about the risk scenario..."
              value={customContext}
              onChange={(e) => setCustomContext(e.target.value)}
              rows={3}
              className="resize-none"
            />
          </div>
        </CardContent>
      </Card>
      
      {/* Generation Controls */}
      <div className="flex space-x-2">
        <Button 
          onClick={generateRisk}
          disabled={isGenerating}
          className="flex items-center space-x-2"
        >
          {isGenerating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Brain className="h-4 w-4" />
          )}
          <span>{isGenerating ? 'Generating...' : 'Generate Risk Statement'}</span>
        </Button>
        
        {generatedRisk && (
          <Button 
            variant="outline"
            onClick={generateRemediation}
            disabled={isGenerating}
            className="flex items-center space-x-2"
          >
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <TrendingUp className="h-4 w-4" />
            )}
            <span>{isGenerating ? 'Generating...' : 'Generate Remediation'}</span>
          </Button>
        )}
      </div>
      
      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {/* Generated Risk Results */}
      {generatedRisk && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                <span>Generated Risk</span>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">
                  {generatedRisk.provider_used || 'Auto-selected'}
                </Badge>
                <Badge 
                  variant={generatedRisk.risk_score >= 7 ? 'destructive' : 
                          generatedRisk.risk_score >= 4 ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  Risk Score: {generatedRisk.risk_score}/10
                </Badge>
              </div>
            </CardTitle>
            <CardDescription>
              AI-generated risk statement based on available data and context
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Risk Statement */}
            {generatedRisk.risk_statement && (
              <div>
                <h4 className="font-medium mb-2">Risk Statement</h4>
                <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                  <p className="text-sm text-orange-800">{generatedRisk.risk_statement}</p>
                </div>
              </div>
            )}
            
            {/* Risk Factors */}
            {generatedRisk.risk_factors && generatedRisk.risk_factors.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Risk Factors</h4>
                <ul className="space-y-2">
                  {generatedRisk.risk_factors.map((factor: string, index: number) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-sm text-gray-600">{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Threat Sources */}
            {generatedRisk.threat_sources && generatedRisk.threat_sources.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Threat Sources</h4>
                <div className="flex flex-wrap gap-2">
                  {generatedRisk.threat_sources.map((source: string, index: number) => (
                    <Badge key={index} variant="destructive" className="text-xs">
                      {source}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            
            {/* Business Impact */}
            {generatedRisk.business_impact && (
              <div>
                <h4 className="font-medium mb-2">Business Impact</h4>
                <div className="bg-red-50 p-3 rounded-lg">
                  <p className="text-sm text-red-800">{generatedRisk.business_impact}</p>
                </div>
              </div>
            )}
            
            {/* Remediation Plan */}
            {generatedRisk.remediation_plan && (
              <div>
                <h4 className="font-medium mb-2 flex items-center space-x-2">
                  <span>Remediation Plan</span>
                  <Badge variant="outline" className="text-xs">
                    {generatedRisk.remediation_provider || 'AI Generated'}
                  </Badge>
                </h4>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="space-y-2">
                    {Array.isArray(generatedRisk.remediation_plan) ? (
                      generatedRisk.remediation_plan.map((step: string, index: number) => (
                        <div key={index} className="flex items-start space-x-2">
                          <span className="bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center mt-0.5">
                            {index + 1}
                          </span>
                          <span className="text-sm text-blue-800">{step}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-blue-800 whitespace-pre-wrap">
                        {generatedRisk.remediation_plan}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            {/* Generation Metadata */}
            <div className="text-xs text-gray-500 pt-2 border-t">
              <div className="flex justify-between items-center">
                <span>Generated at {new Date(generatedRisk.timestamp || Date.now()).toLocaleString()}</span>
                {generatedRisk.cost && (
                  <span>Cost: ${generatedRisk.cost.toFixed(6)}</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RiskGenerator;