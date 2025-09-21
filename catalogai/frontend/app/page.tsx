'use client';

import { useState } from 'react';
import { Uploader } from './components/Uploader';
import { ScoreBadge, ScoreBar } from './components/ScoreBadge';
import { apiClient, type ScanResult, formatProcessingTime } from './api';
import { Sparkles, Shield, Zap, Eye, Palette, Layers, Target, Lightbulb } from 'lucide-react';

export default function HomePage() {
  const [isScanning, setIsScanning] = useState(false);
  const [results, setResults] = useState<ScanResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [totalTime, setTotalTime] = useState<number>(0);

  const handleFilesSelected = async (files: File[]) => {
    if (files.length === 0) {
      setResults([]);
      return;
    }

    setIsScanning(true);
    setError(null);
    setResults([]);

    try {
      const response = await apiClient.scanImages(files);
      setResults(response.results);
      setTotalTime(response.total_time_ms);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during scanning');
      console.error('Scan error:', err);
    } finally {
      setIsScanning(false);
    }
  };

  const getGuidanceMessage = (label: string): string => {
    switch (label) {
      case 'synthetic':
        return 'Needs Real Proof — Consider uploading real-world photos (multiple angles, material close-ups, scale references). Avoid oversmoothing and uniform lighting.';
      case 'suspicious':
        return 'Looks Suspicious — Lighting/texture patterns are atypical. Add more real photos to increase confidence.';
      case 'authentic':
        return 'Verified — Signals look consistent with real photography.';
      default:
        return 'Analysis completed. Please review the results.';
    }
  };

  const getGuidanceIcon = (label: string) => {
    switch (label) {
      case 'synthetic': return <Shield className="w-5 h-5 text-danger-600" />;
      case 'suspicious': return <Eye className="w-5 h-5 text-warning-600" />;
      case 'authentic': return <Sparkles className="w-5 h-5 text-success-600" />;
      default: return <Target className="w-5 h-5 text-neutral-600" />;
    }
  };

  return (
    <div className="min-h-screen">
      <section className="hero-section section-spacing relative">
        <div className="container-responsive">
          <div className="text-center max-w-4xl mx-auto">
            <div className="flex justify-center mb-8">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-3xl blur-xl opacity-20 animate-pulse-soft"></div>
                <div className="relative bg-gradient-to-r from-primary-600 to-secondary-600 p-6 rounded-3xl shadow-large float">
                  <Sparkles className="w-12 h-12 text-white" />
                </div>
              </div>
            </div>

            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in">
              <span className="gradient-text">Image Authenticity</span>
              <br />
              <span className="text-neutral-800">Detection</span>
            </h1>

            <p className="text-xl md:text-2xl text-neutral-600 mb-8 max-w-3xl mx-auto text-balance animate-slide-up">
              Advanced AI-powered analysis to detect synthetic and AI-generated content in product images. 
              Protect your marketplace with cutting-edge authenticity verification.
            </p>

            <div className="flex flex-wrap justify-center gap-4 mb-12 animate-slide-up">
              <div className="glass rounded-full px-6 py-3 flex items-center space-x-2 hover-lift">
                <Zap className="w-4 h-4 text-success-600" />
                <span className="text-sm font-medium text-neutral-700">Real-time Analysis</span>
              </div>
              <div className="glass rounded-full px-6 py-3 flex items-center space-x-2 hover-lift">
                <Shield className="w-4 h-4 text-primary-600" />
                <span className="text-sm font-medium text-neutral-700">99%+ Accuracy</span>
              </div>
              <div className="glass rounded-full px-6 py-3 flex items-center space-x-2 hover-lift">
                <Sparkles className="w-4 h-4 text-secondary-600" />
                <span className="text-sm font-medium text-neutral-700">Instant Results</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="container-responsive space-y-12 pb-20">
        <section className="animate-slide-up">
          <div className="card-elevated p-8 hover-scale">
            <div className="text-center mb-8">
              <h2 className="title-xl mb-3">
                Upload Images for Analysis
              </h2>
              <p className="subtitle">
                Drag and drop your images or click to browse
              </p>
            </div>
            <Uploader
              onFilesSelected={handleFilesSelected}
              isUploading={isScanning}
              maxFiles={10}
              maxFileSize={8}
            />
          </div>
        </section>

        {error && (
          <section className="animate-slide-down">
            <div className="notification-error">
              <div className="flex items-start space-x-3">
                <Shield className="w-6 h-6 text-danger-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-danger-800 mb-1">Analysis Error</h3>
                  <p className="text-danger-700">{error}</p>
                </div>
              </div>
            </div>
          </section>
        )}

        {results.length > 0 && (
          <section className="space-y-8 animate-fade-in">
            <div className="card-elevated p-8">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
                <div>
                  <h2 className="text-2xl lg:text-3xl font-bold text-neutral-900 mb-2">
                    Analysis Results
                  </h2>
                  <p className="text-neutral-600 text-lg">
                    Processed {results.length} images in {formatProcessingTime(totalTime)}
                  </p>
                </div>
                <div className="mt-4 lg:mt-0">
                  <div className="badge-success flex items-center space-x-2 px-4 py-2">
                    <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                    <span className="font-medium">Analysis Complete</span>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                {results.map((result: any, index: number) => (
                  <div key={index} className="card hover-lift p-6">
                    <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
                      <div className="xl:col-span-4">
                        <div className="flex items-center space-x-4">
                          <div className="p-3 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-2xl">
                            <Layers className="w-6 h-6 text-primary-600" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="font-semibold text-neutral-900 truncate text-lg">
                              {result.filename}
                            </div>
                            <div className="flex items-center space-x-3 text-sm text-neutral-500 mt-1">
                              <span className="flex items-center space-x-1">
                                <Layers className="w-3 h-3" />
                                <span>{(result.size / 1024).toFixed(1)} KB</span>
                              </span>
                              {result.processing_time_ms && (
                                <span className="flex items-center space-x-1">
                                  <Zap className="w-3 h-3" />
                                  <span>{formatProcessingTime(result.processing_time_ms)}</span>
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="xl:col-span-3">
                        <div className="space-y-4">
                          <ScoreBadge label={result.label} score={result.score} />
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="font-medium text-neutral-700">Confidence</span>
                              <span className="font-bold text-neutral-900">
                                {(result.score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <ScoreBar score={result.score} />
                          </div>
                        </div>
                      </div>

                      <div className="xl:col-span-5 space-y-4">
                        <div className="glass-strong p-4 rounded-xl">
                          <div className="flex items-start space-x-3 mb-3">
                            {getGuidanceIcon(result.label)}
                            <div>
                              <div className="font-semibold text-neutral-900 mb-2">Guidance</div>
                              <div className="text-sm text-neutral-700 leading-relaxed">
                                {getGuidanceMessage(result.label)}
                              </div>
                            </div>
                          </div>
                        </div>

                        {result.reasons.length > 0 && (
                          <div className="glass p-4 rounded-xl">
                            <div className="flex items-center space-x-2 mb-3">
                              <Eye className="w-4 h-4 text-primary-600" />
                              <div className="font-semibold text-neutral-900">Technical Analysis</div>
                            </div>
                            <ul className="space-y-2">
                              {result.reasons.slice(0, 3).map((reason: string, reasonIndex: number) => (
                                <li key={reasonIndex} className="flex items-start space-x-2 text-sm">
                                  <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                                  <span className="text-neutral-700 leading-relaxed">{reason}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card-elevated p-8 hover-scale">
              <h3 className="text-2xl font-bold text-neutral-900 mb-8 text-center">
                Analysis Summary
              </h3>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                {['authentic', 'suspicious', 'synthetic', 'error'].map((label) => {
                  const count = results.filter((r: any) => r.label === label).length;
                  const percentage = results.length > 0 ? (count / results.length) * 100 : 0;
                  
                  const getStatColor = (label: string) => {
                    switch (label) {
                      case 'authentic': return 'from-success-500 to-accent-500';
                      case 'suspicious': return 'from-warning-500 to-warning-600';
                      case 'synthetic': return 'from-danger-500 to-danger-600';
                      default: return 'from-neutral-400 to-neutral-500';
                    }
                  };

                  const getStatIcon = (label: string) => {
                    switch (label) {
                      case 'authentic': return <Sparkles className="w-8 h-8 text-success-600" />;
                      case 'suspicious': return <Eye className="w-8 h-8 text-warning-600" />;
                      case 'synthetic': return <Shield className="w-8 h-8 text-danger-600" />;
                      default: return <Target className="w-8 h-8 text-neutral-600" />;
                    }
                  };
                  
                  return (
                    <div key={label} className="stats-card hover-lift">
                      <div className="mb-4">{getStatIcon(label)}</div>
                      <div className={`text-3xl font-bold bg-gradient-to-r ${getStatColor(label)} bg-clip-text text-transparent mb-2`}>
                        {count}
                      </div>
                      <div className="font-semibold text-neutral-700 capitalize mb-1">{label}</div>
                      <div className="text-sm text-neutral-500">{percentage.toFixed(1)}% of total</div>
                      <div className="mt-3 w-full bg-neutral-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full bg-gradient-to-r ${getStatColor(label)} transition-all duration-1000`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        <section className="animate-slide-up">
          <div className="card-elevated p-8 lg:p-12">
            <div className="text-center mb-12">
              <h3 className="text-2xl lg:text-3xl font-bold text-neutral-900 mb-4">
                How Our AI Detection Works
              </h3>
              <p className="text-lg text-neutral-600 max-w-3xl mx-auto text-balance">
                Our advanced machine learning system analyzes multiple image characteristics to detect synthetic content with industry-leading accuracy
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
              <div className="card-interactive text-center p-6">
                <div className="mb-4">
                  <Eye className="w-8 h-8 text-primary-600 mx-auto" />
                </div>
                <h4 className="font-semibold text-neutral-900 mb-2">Edge Analysis</h4>
                <p className="text-sm text-neutral-600">Examines edge patterns and sharpness characteristics</p>
              </div>
              <div className="card-interactive text-center p-6">
                <div className="mb-4">
                  <Palette className="w-8 h-8 text-secondary-600 mx-auto" />
                </div>
                <h4 className="font-semibold text-neutral-900 mb-2">Color Distribution</h4>
                <p className="text-sm text-neutral-600">Analyzes color patterns and saturation uniformity</p>
              </div>
              <div className="card-interactive text-center p-6">
                <div className="mb-4">
                  <Layers className="w-8 h-8 text-accent-600 mx-auto" />
                </div>
                <h4 className="font-semibold text-neutral-900 mb-2">Compression Artifacts</h4>
                <p className="text-sm text-neutral-600">Detects compression patterns and noise signatures</p>
              </div>
              <div className="card-interactive text-center p-6">
                <div className="mb-4">
                  <Target className="w-8 h-8 text-warning-600 mx-auto" />
                </div>
                <h4 className="font-semibold text-neutral-900 mb-2">Texture Analysis</h4>
                <p className="text-sm text-neutral-600">Evaluates texture patterns and lighting consistency</p>
              </div>
            </div>

            <div className="notification-info">
              <div className="flex items-start space-x-4">
                <Lightbulb className="w-6 h-6 text-primary-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-primary-800 mb-2">Important Note</h4>
                  <p className="text-primary-700 leading-relaxed">
                    This tool provides AI-powered suggestions to help improve your image authenticity detection. 
                    While our system achieves high accuracy, human review is always recommended for final decisions 
                    in critical applications.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}