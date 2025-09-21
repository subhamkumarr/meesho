'use client';

import { useState, useEffect } from 'react';
import { ScoreBar } from './ScoreBadge';
import { apiClient, type ThresholdsOut, type ThresholdsIn } from '../api';

interface ThresholdEditorProps {
  onThresholdsChange?: (thresholds: ThresholdsOut) => void;
}

export function ThresholdEditor({ onThresholdsChange }: ThresholdEditorProps) {
  const [thresholds, setThresholds] = useState<ThresholdsOut | null>(null);
  const [editingThresholds, setEditingThresholds] = useState<ThresholdsIn>({
    thresh_auth: 0.15,
    thresh_syn: 0.70,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Sample scores for preview
  const sampleScores = [0.05, 0.12, 0.25, 0.45, 0.65, 0.78, 0.92];

  useEffect(() => {
    loadThresholds();
  }, []);

  const loadThresholds = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getThresholds();
      setThresholds(data);
      setEditingThresholds({
        thresh_auth: data.thresh_auth,
        thresh_syn: data.thresh_syn,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load thresholds');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);

      // Validate thresholds
      if (editingThresholds.thresh_syn <= editingThresholds.thresh_auth) {
        throw new Error('Synthetic threshold must be greater than authentic threshold');
      }

      const updatedThresholds = await apiClient.updateThresholds(editingThresholds);
      setThresholds(updatedThresholds);
      setSuccessMessage('Thresholds updated successfully');
      onThresholdsChange?.(updatedThresholds);

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update thresholds');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (thresholds) {
      setEditingThresholds({
        thresh_auth: thresholds.thresh_auth,
        thresh_syn: thresholds.thresh_syn,
      });
    }
    setError(null);
    setSuccessMessage(null);
  };

  const getClassificationLabel = (score: number): string => {
    if (score < editingThresholds.thresh_auth) return 'authentic';
    if (score < editingThresholds.thresh_syn) return 'suspicious';
    return 'synthetic';
  };

  const hasChanges = thresholds && (
    editingThresholds.thresh_auth !== thresholds.thresh_auth ||
    editingThresholds.thresh_syn !== thresholds.thresh_syn
  );

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-center py-8">
          <div className="loading-spinner mr-3" />
          <span>Loading thresholds...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Threshold Configuration</h2>

      {/* Current Thresholds Info */}
      {thresholds && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-600 mb-2">
            Last updated: {new Date(thresholds.updated_at).toLocaleString()} by {thresholds.updated_by}
          </div>
          <div className="text-sm text-gray-700">
            Current: Authentic &lt; {(thresholds.thresh_auth * 100).toFixed(1)}% &lt; Suspicious &lt; {(thresholds.thresh_syn * 100).toFixed(1)}% &lt; Synthetic
          </div>
        </div>
      )}

      {/* Error/Success Messages */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex">
            <span className="text-red-400 text-lg mr-2">⚠️</span>
            <span className="text-sm text-red-700">{error}</span>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex">
            <span className="text-green-400 text-lg mr-2">✅</span>
            <span className="text-sm text-green-700">{successMessage}</span>
          </div>
        </div>
      )}

      {/* Threshold Controls */}
      <div className="space-y-6">
        {/* Authentic Threshold */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Authentic Threshold ({(editingThresholds.thresh_auth * 100).toFixed(1)}%)
          </label>
          <div className="space-y-2">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={editingThresholds.thresh_auth}
              onChange={(e) => setEditingThresholds(prev => ({
                ...prev,
                thresh_auth: parseFloat(e.target.value)
              }))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Images with synthetic probability below this threshold are classified as authentic.
          </p>
        </div>

        {/* Synthetic Threshold */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Synthetic Threshold ({(editingThresholds.thresh_syn * 100).toFixed(1)}%)
          </label>
          <div className="space-y-2">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={editingThresholds.thresh_syn}
              onChange={(e) => setEditingThresholds(prev => ({
                ...prev,
                thresh_syn: parseFloat(e.target.value)
              }))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Images with synthetic probability above this threshold are classified as synthetic.
          </p>
        </div>

        {/* Preview */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Live Preview</h3>
          <div className="space-y-3">
            {sampleScores.map((score, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className="w-16 text-sm text-gray-600">
                  {(score * 100).toFixed(1)}%
                </div>
                <div className="flex-1">
                  <ScoreBar 
                    score={score} 
                    thresholds={{
                      auth: editingThresholds.thresh_auth,
                      syn: editingThresholds.thresh_syn
                    }}
                  />
                </div>
                <div className="w-24 text-sm">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    getClassificationLabel(score) === 'authentic' 
                      ? 'bg-green-100 text-green-700'
                      : getClassificationLabel(score) === 'suspicious'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {getClassificationLabel(score)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-6 border-t">
          <button
            onClick={handleReset}
            disabled={!hasChanges || isSaving}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Reset
          </button>
          <button
            onClick={handleSave}
            disabled={!hasChanges || isSaving}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isSaving && <div className="loading-spinner mr-2 h-4 w-4" />}
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}