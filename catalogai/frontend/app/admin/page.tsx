'use client';

import { useState, useEffect } from 'react';
import { ThresholdEditor } from '../components/ThresholdEditor';
import { apiClient, type TrainingResponse, type ThresholdsOut } from '../api';

export default function AdminPage() {
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<TrainingResponse | null>(null);
  const [modelMetrics, setModelMetrics] = useState<any>(null);
  const [isLoadingMetrics, setIsLoadingMetrics] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadModelMetrics();
  }, []);

  const loadModelMetrics = async () => {
    try {
      setIsLoadingMetrics(true);
      const metrics = await apiClient.getModelMetrics();
      setModelMetrics(metrics);
    } catch (err) {
      console.error('Failed to load model metrics:', err);
      // Don't show error for metrics - it's optional
    } finally {
      setIsLoadingMetrics(false);
    }
  };

  const handleRetrain = async () => {
    try {
      setIsTraining(true);
      setError(null);
      setTrainingResult(null);

      const result = await apiClient.retrainModel();
      setTrainingResult(result);

      if (result.success) {
        // Reload metrics after successful training
        await loadModelMetrics();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Training failed');
    } finally {
      setIsTraining(false);
    }
  };

  const handleThresholdsChange = (thresholds: ThresholdsOut) => {
    // Could trigger any additional actions when thresholds change
    console.log('Thresholds updated:', thresholds);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="card p-4">
        <h1 className="title-xl">Admin Panel</h1>
        <p className="mt-2 subtitle">
          Manage model thresholds and retrain the authenticity detection system
        </p>
      </div>

      {/* Threshold Configuration */}
      <ThresholdEditor onThresholdsChange={handleThresholdsChange} />

      {/* Model Management */}
      <div className="card-elevated p-6 hover-scale">
        <h2 className="text-xl font-semibold text-neutral-900 mb-6">Model Management</h2>

        {/* Current Model Metrics */}
        {!isLoadingMetrics && modelMetrics && (
          <div className="mb-6 p-4 glass rounded-xl">
            <h3 className="text-lg font-medium text-neutral-900 mb-3">Current Model Performance</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {(modelMetrics.accuracy * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-neutral-600">Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {modelMetrics.n_train_samples || 0}
                </div>
                <div className="text-sm text-neutral-600">Training Samples</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {modelMetrics.n_features || 0}
                </div>
                <div className="text-sm text-neutral-600">Features</div>
              </div>
            </div>
            
            {modelMetrics.training_time_seconds && (
              <div className="mt-3 text-sm text-neutral-600 text-center">
                Last trained in {modelMetrics.training_time_seconds.toFixed(1)} seconds
              </div>
            )}
          </div>
        )}

        {/* Training Section */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium text-neutral-900 mb-2">Retrain Model</h3>
            <p className="text-sm text-neutral-600 mb-4">
              Retrain the authenticity detection model using the latest seed data. 
              This will generate new synthetic and realistic images for training.
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="notification-error">
              <div className="flex">
                <span className="text-danger-400 text-lg mr-2">⚠️</span>
                <div>
                  <h4 className="text-sm font-medium">Training Error</h4>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Training Result */}
          {trainingResult && (
            <div className={`p-4 rounded-xl border ${
              trainingResult.success 
                ? 'bg-green-50 border-green-200' 
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex">
                <span className={`text-lg mr-2 ${
                  trainingResult.success ? 'text-green-400' : 'text-red-400'
                }`}>
                  {trainingResult.success ? '✅' : '❌'}
                </span>
                <div className="flex-1">
                  <h4 className={`text-sm font-medium ${
                    trainingResult.success ? 'text-green-800' : 'text-red-800'
                  }`}>
                    {trainingResult.success ? 'Training Successful' : 'Training Failed'}
                  </h4>
                  <p className={`text-sm mt-1 ${
                    trainingResult.success ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {trainingResult.message}
                  </p>
                  
                  {trainingResult.success && trainingResult.metrics && (
                    <div className="mt-3 space-y-2">
                      <div className="text-sm text-green-700">
                        <strong>New Model Metrics:</strong>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          Accuracy: <strong>{(trainingResult.metrics.accuracy * 100).toFixed(1)}%</strong>
                        </div>
                        <div>
                          Training Time: <strong>{(trainingResult.training_time_ms / 1000).toFixed(1)}s</strong>
                        </div>
                        <div>
                          Train Samples: <strong>{trainingResult.metrics.n_train_samples}</strong>
                        </div>
                        <div>
                          Test Samples: <strong>{trainingResult.metrics.n_test_samples}</strong>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Training Button */}
          <div className="flex justify-start">
            <button
              onClick={handleRetrain}
              disabled={isTraining}
              className="btn-primary btn-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isTraining && <div className="loading-spinner mr-3 h-5 w-5" />}
              {isTraining ? 'Training Model...' : 'Retrain Model'}
            </button>
          </div>

          {isTraining && (
            <div className="text-sm text-neutral-600">
              ⏳ This may take 1-2 minutes. The model will generate training data and retrain automatically.
            </div>
          )}
        </div>
      </div>

      {/* Help Section */}
      <div className="notification-info">
        <div>
        <h3 className="text-lg font-medium mb-2">Admin Guide</h3>
        <div className="text-sm space-y-2">
          <p><strong>Threshold Configuration:</strong></p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li><strong>Authentic Threshold:</strong> Lower values make the system more strict (fewer images classified as authentic)</li>
            <li><strong>Synthetic Threshold:</strong> Higher values make the system more conservative (fewer images classified as synthetic)</li>
            <li>Images between thresholds are classified as "suspicious" and require human review</li>
          </ul>
          
          <p className="mt-4"><strong>Model Retraining:</strong></p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li>Generates fresh synthetic and realistic training images</li>
            <li>Retrains the SVM classifier with balanced class weights</li>
            <li>Updates model artifacts and performance metrics</li>
            <li>Changes take effect immediately after successful training</li>
          </ul>
        </div>
        </div>
      </div>
    </div>
  );
}