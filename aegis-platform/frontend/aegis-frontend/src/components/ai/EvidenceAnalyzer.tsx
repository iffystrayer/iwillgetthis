import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Loader2, FileText, Brain, CheckCircle, AlertTriangle } from 'lucide-react';
import ProviderSelector from './ProviderSelector';
import { aiApi } from '../../lib/api';
import { EvidenceAnalysisResponse, NarrativeResponse } from '../../types/ai';

interface EvidenceAnalyzerProps {
  evidenceId?: string;
  evidenceContent?: string;
  onAnalysisComplete?: (analysis: any) => void;
  className?: string;
}

const EvidenceAnalyzer: React.FC<EvidenceAnalyzerProps> = ({
  evidenceId,
  evidenceContent,
  onAnalysisComplete,
  className = ''
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<EvidenceAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string | undefined>(undefined);
  const [customContent, setCustomContent] = useState('');

  const analyzeEvidence = async () => {
    if (!evidenceContent && !customContent) {
      setError('No evidence content to analyze');
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      
      const response = await aiApi.analyzeEvidenceEnhanced({
        evidence_id: evidenceId,
        evidence_content: evidenceContent || customContent,
        preferred_provider: selectedProvider,
        analysis_type: 'comprehensive'
      }) as EvidenceAnalysisResponse;
      
      setAnalysis(response);
      onAnalysisComplete?.(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze evidence');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const generateNarrative = async () => {
    if (!analysis) {
      setError('No analysis available to generate narrative from');
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      
      const response = await aiApi.generateNarrativeEnhanced({
        evidence_id: evidenceId,
        analysis_summary: analysis.summary,
        key_findings: analysis.key_findings,
        preferred_provider: selectedProvider
      }) as NarrativeResponse;
      
      setAnalysis(prev => ({
        ...prev!,
        generated_narrative: response.narrative,
        narrative_provider: response.provider_used
      }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate narrative');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Provider Selection */}
      <ProviderSelector
        taskType="evidence_analysis"
        selectedProvider={selectedProvider}
        onProviderChange={setSelectedProvider}
      />
      
      {/* Evidence Input (if no content provided) */}
      {!evidenceContent && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>Evidence Content</span>
            </CardTitle>
            <CardDescription>
              Paste or type the evidence content you want to analyze
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="Paste evidence content here (policy text, procedure document, etc.)..."
              value={customContent}
              onChange={(e) => setCustomContent(e.target.value)}
              rows={6}
              className="resize-none"
            />
          </CardContent>
        </Card>
      )}
      
      {/* Analysis Controls */}
      <div className="flex space-x-2">
        <Button 
          onClick={analyzeEvidence}
          disabled={isAnalyzing || (!evidenceContent && !customContent)}
          className="flex items-center space-x-2"
        >
          {isAnalyzing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Brain className="h-4 w-4" />
          )}
          <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Evidence'}</span>
        </Button>
        
        {analysis && (
          <Button 
            variant="outline"
            onClick={generateNarrative}
            disabled={isAnalyzing}
            className="flex items-center space-x-2"
          >
            {isAnalyzing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            <span>{isAnalyzing ? 'Generating...' : 'Generate Narrative'}</span>
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
      
      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Analysis Results</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {analysis.provider_used || 'Auto-selected'}
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    {analysis.response_time?.toFixed(2)}s
                  </Badge>
                </div>
              </CardTitle>
              <CardDescription>
                AI-powered analysis of the evidence content
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Summary */}
              {analysis.summary && (
                <div>
                  <h4 className="font-medium mb-2">Summary</h4>
                  <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                    {analysis.summary}
                  </p>
                </div>
              )}
              
              {/* Key Findings */}
              {analysis.key_findings && analysis.key_findings.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Key Findings</h4>
                  <ul className="space-y-2">
                    {analysis.key_findings.map((finding: string, index: number) => (
                      <li key={index} className="flex items-start space-x-2">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                        <span className="text-sm text-gray-600">{finding}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Control Mappings */}
              {analysis.control_mappings && analysis.control_mappings.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Relevant Controls</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.control_mappings.map((control: string, index: number) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {control}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Compliance Assessment */}
              {analysis.compliance_assessment && (
                <div>
                  <h4 className="font-medium mb-2">Compliance Assessment</h4>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-sm text-blue-800">{analysis.compliance_assessment}</p>
                  </div>
                </div>
              )}
              
              {/* Generated Narrative */}
              {analysis.generated_narrative && (
                <div>
                  <h4 className="font-medium mb-2 flex items-center space-x-2">
                    <span>Generated Control Narrative</span>
                    <Badge variant="outline" className="text-xs">
                      {analysis.narrative_provider || 'AI Generated'}
                    </Badge>
                  </h4>
                  <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <p className="text-sm text-green-800 whitespace-pre-wrap">
                      {analysis.generated_narrative}
                    </p>
                  </div>
                </div>
              )}
              
              {/* Analysis Metadata */}
              <div className="text-xs text-gray-500 pt-2 border-t">
                <div className="flex justify-between items-center">
                  <span>Analysis completed at {new Date(analysis.timestamp || Date.now()).toLocaleString()}</span>
                  {analysis.cost && (
                    <span>Cost: ${analysis.cost.toFixed(6)}</span>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default EvidenceAnalyzer;