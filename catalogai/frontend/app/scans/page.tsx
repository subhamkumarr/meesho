'use client';

import { useState, useEffect, useCallback } from 'react';
import { ScoreBadge } from '../components/ScoreBadge';
import { apiClient, type ScanOut, formatFileSize } from '../api';

export default function ScansPage() {
  const [scans, setScans] = useState<ScanOut[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [total, setTotal] = useState(0);
  const [selectedScan, setSelectedScan] = useState<ScanOut | null>(null);

  const loadScans = useCallback(async (page: number = 1, append: boolean = false) => {
    try {
      if (page === 1) {
        setIsLoading(true);
      } else {
        setIsLoadingMore(true);
      }
      setError(null);

      const response = await apiClient.getScans(page, 20);
      
      if (append) {
        setScans(prev => [...prev, ...response.scans]);
      } else {
        setScans(response.scans);
      }
      
      setCurrentPage(page);
      setHasNext(response.has_next);
      setTotal(response.total);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scans');
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  }, []);

  useEffect(() => {
    loadScans(1);
  }, [loadScans]);

  const handleLoadMore = () => {
    if (hasNext && !isLoadingMore) {
      loadScans(currentPage + 1, true);
    }
  };

  const handleRefresh = () => {
    loadScans(1);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getScanSummary = () => {
    const summary = scans.reduce((acc, scan) => {
      acc[scan.label] = (acc[scan.label] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return summary;
  };

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Scan History</h1>
          <p className="mt-2 text-lg text-neutral-600">Review past authenticity scans</p>
        </div>
        
        <div className="card-elevated p-8">
          <div className="flex items-center justify-center">
            <div className="loading-spinner mr-3" />
            <span>Loading scan history...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start card p-4">
        <div>
          <h1 className="title-xl">Scan History</h1>
          <p className="mt-2 subtitle">
            {total > 0 ? `${total} total scans` : 'No scans found'}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="btn-primary btn-md hover-scale"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="notification-error">
          <div className="flex">
            <span className="text-danger-400 text-lg mr-2">⚠️</span>
            <div>
              <h3 className="text-sm font-medium">Error</h3>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      {scans.length > 0 && (
        <div className="card-elevated p-6">
          <h2 className="text-lg font-medium text-neutral-900 mb-4">Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(getScanSummary()).map(([label, count]) => (
              <div key={label} className="stats-card">
                <div className="text-2xl font-bold text-neutral-900">{count}</div>
                <div className="text-sm text-neutral-600 capitalize">{label}</div>
                <div className="text-xs text-neutral-500">
                  {((count / scans.length) * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Scans Table */}
      {scans.length > 0 ? (
        <div className="card-elevated overflow-hidden">
          <div className="px-6 py-4 border-b border-neutral-200">
            <h2 className="text-lg font-medium text-neutral-900">Recent Scans</h2>
          </div>
          
          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>File</th>
                  <th>Result</th>
                  <th>Score</th>
                  <th>Size</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {scans.map((scan) => (
                  <tr key={scan.id} className="hover:bg-neutral-50">
                    <td>
                      <div className="flex items-center">
                        <span className="text-lg mr-2">🖼️</span>
                        <div>
                          <div className="text-sm font-medium text-neutral-900 truncate max-w-xs">
                            {scan.filename}
                          </div>
                          <div className="text-xs text-neutral-500">
                            ID: {scan.id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <ScoreBadge label={scan.label} score={scan.score} />
                    </td>
                    <td>
                      <div className="text-sm text-neutral-900">
                        {(scan.score * 100).toFixed(1)}%
                      </div>
                    </td>
                    <td>
                      <div className="text-sm text-neutral-900">
                        {formatFileSize(scan.size)}
                      </div>
                      <div className="text-xs text-neutral-500">
                        {scan.mime_type}
                      </div>
                    </td>
                    <td>
                      <div className="text-sm text-neutral-900">
                        {formatDate(scan.created_at)}
                      </div>
                    </td>
                    <td>
                      <button
                        onClick={() => setSelectedScan(scan)}
                        className="btn-secondary btn-sm"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Load More Button */}
          {hasNext && (
            <div className="px-6 py-4 border-t border-neutral-200 text-center">
              <button
                onClick={handleLoadMore}
                disabled={isLoadingMore}
                className="btn-secondary btn-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center mx-auto"
              >
                {isLoadingMore && <div className="loading-spinner mr-2 h-4 w-4" />}
                {isLoadingMore ? 'Loading...' : 'Load More'}
              </button>
            </div>
          )}
        </div>
      ) : !isLoading && (
        <div className="card-elevated p-8 text-center">
          <div className="text-4xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-neutral-900 mb-2">No scans found</h3>
          <p className="text-neutral-600 mb-4">
            Upload some images to see scan results here.
          </p>
          <a
            href="/"
            className="btn-primary"
          >
            📤 Upload Images
          </a>
        </div>
      )}

      {/* Scan Details Modal */}
      {selectedScan && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
          <div className="card-elevated max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-medium text-neutral-900">Scan Details</h3>
                <button
                  onClick={() => setSelectedScan(null)}
                  className="btn-ghost text-xl"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                {/* File Info */}
                <div className="grid grid-cols-2 gap-4 p-4 glass rounded-xl">
                  <div>
                    <div className="text-sm font-medium text-neutral-700">Filename</div>
                    <div className="text-sm text-neutral-900">{selectedScan.filename}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-neutral-700">Size</div>
                    <div className="text-sm text-neutral-900">{formatFileSize(selectedScan.size)}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-neutral-700">Type</div>
                    <div className="text-sm text-neutral-900">{selectedScan.mime_type}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-neutral-700">Scanned</div>
                    <div className="text-sm text-neutral-900">{formatDate(selectedScan.created_at)}</div>
                  </div>
                </div>

                {/* Result */}
                <div>
                  <div className="text-sm font-medium text-neutral-700 mb-2">Result</div>
                  <ScoreBadge label={selectedScan.label} score={selectedScan.score} />
                </div>

                {/* Reasons */}
                {selectedScan.reasons.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-neutral-700 mb-2">Analysis Details</div>
                    <ul className="space-y-2">
                      {selectedScan.reasons.map((reason, index) => (
                        <li key={index} className="flex items-start text-sm text-neutral-600">
                          <span className="text-neutral-400 mr-2">•</span>
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Technical Info */}
                <div className="p-4 glass rounded-xl">
                  <div className="text-sm font-medium text-neutral-700 mb-2">Technical Details</div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-neutral-600">Scan ID:</span> {selectedScan.id}
                    </div>
                    <div>
                      <span className="text-neutral-600">Features Hash:</span> {selectedScan.features_hash.substring(0, 8)}...
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setSelectedScan(null)}
                  className="btn-secondary btn-sm"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}