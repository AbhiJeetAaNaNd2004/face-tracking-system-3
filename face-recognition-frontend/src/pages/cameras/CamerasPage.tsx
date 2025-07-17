import React, { useState, useEffect } from 'react';
import { Camera, Grid, List, RefreshCw, AlertTriangle } from 'lucide-react';
import CameraFeed from '../../components/common/CameraFeed';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const CamerasPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [streamStatus, setStreamStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // For demo purposes, we'll show cameras 0-3
  const cameraIds = [0, 1, 2, 3];

  const fetchStreamStatus = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const status = await apiService.getStreamStatus();
      setStreamStatus(status);
    } catch (err: any) {
      console.error('Stream status error:', err);
      setError('Stream status unavailable');
      // Set default values for demo
      setStreamStatus({
        total_active_streams: 0,
        max_concurrent_streams: 5,
        available_slots: 5
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStreamStatus();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStreamStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Loading camera feeds..." />;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Camera Feeds
          </h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">
            Real-time monitoring and surveillance
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md ${
                viewMode === 'grid'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}
              title="Grid view"
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md ${
                viewMode === 'list'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}
              title="List view"
            >
              <List className="h-4 w-4" />
            </button>
          </div>
          <button
            onClick={fetchStreamStatus}
            disabled={isLoading}
            className="btn-secondary flex items-center"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* System Status */}
      {streamStatus && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            System Overview
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {streamStatus.total_active_streams}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Active Streams
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {streamStatus.max_concurrent_streams}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Max Concurrent
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {streamStatus.available_slots}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Available Slots
              </div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400 mr-2" />
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Camera Feeds */}
      <div className={
        viewMode === 'grid' 
          ? 'grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-2 gap-6'
          : 'space-y-6'
      }>
        {cameraIds.map((cameraId) => (
          <CameraFeed
            key={cameraId}
            cameraId={cameraId}
            title={`Camera ${cameraId + 1} - ${getCameraLocation(cameraId)}`}
            className={viewMode === 'list' ? 'max-w-md' : ''}
          />
        ))}
      </div>

      {/* Instructions */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Camera System Instructions
        </h3>
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ul className="text-gray-600 dark:text-gray-400 space-y-2">
            <li>
              <strong>Starting Streams:</strong> Click the "Start Stream" button on any camera feed to begin real-time monitoring.
            </li>
            <li>
              <strong>System Limits:</strong> The system supports up to {streamStatus?.max_concurrent_streams || 5} concurrent streams to maintain performance.
            </li>
            <li>
              <strong>Camera Status:</strong> Green indicator shows camera is available, red indicates unavailable or disconnected.
            </li>
            <li>
              <strong>Face Detection:</strong> Active streams automatically perform face recognition and attendance tracking.
            </li>
            <li>
              <strong>Quality Settings:</strong> Streams are optimized for real-time performance with face detection overlays.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// Helper function to get camera location names
function getCameraLocation(cameraId: number): string {
  const locations = [
    'Main Entrance',
    'Reception Area', 
    'Conference Room',
    'Exit Door'
  ];
  return locations[cameraId] || 'Unknown Location';
}

export default CamerasPage;