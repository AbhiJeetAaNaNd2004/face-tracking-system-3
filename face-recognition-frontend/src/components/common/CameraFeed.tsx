import React, { useState, useRef, useEffect } from 'react';
import { Camera, AlertTriangle, RefreshCw, Maximize2 } from 'lucide-react';
import apiService from '../../services/api';
import { CameraStatus } from '../../types/common';

interface CameraFeedProps {
  cameraId: number;
  title?: string;
  className?: string;
  autoStart?: boolean;
}

const CameraFeed: React.FC<CameraFeedProps> = ({ 
  cameraId, 
  title, 
  className = '',
  autoStart = false 
}) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameraStatus, setCameraStatus] = useState<CameraStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  const checkCameraStatus = async () => {
    try {
      const status = await apiService.getCameraStatus(cameraId);
      setCameraStatus(status);
      if (!status.is_available) {
        setError('Camera is not available');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to check camera status');
    }
  };

  const startStream = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      await checkCameraStatus();
      
      if (imgRef.current) {
        const streamUrl = apiService.getCameraStreamUrl(cameraId);
        const token = localStorage.getItem('access_token');
        const urlWithAuth = `${streamUrl}?token=${encodeURIComponent(token || '')}`;
        imgRef.current.src = urlWithAuth;
        setIsStreaming(true);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to start camera stream');
    } finally {
      setIsLoading(false);
    }
  };

  const stopStream = () => {
    if (imgRef.current) {
      imgRef.current.src = '';
    }
    setIsStreaming(false);
  };

  const handleImageError = () => {
    setError('Failed to load camera stream');
    setIsStreaming(false);
  };

  const handleImageLoad = () => {
    setError(null);
  };

  useEffect(() => {
    if (autoStart) {
      startStream();
    }
    
    // Cleanup on unmount
    return () => {
      stopStream();
    };
  }, [cameraId, autoStart]);

  return (
    <div className={`card ${className}`}>
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            {title || `Camera ${cameraId}`}
          </h3>
          <div className="flex items-center space-x-2">
            {cameraStatus && (
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                cameraStatus.is_available 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                  : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
              }`}>
                <span className={`w-2 h-2 rounded-full mr-1 ${
                  cameraStatus.is_available ? 'bg-green-400' : 'bg-red-400'
                }`}></span>
                {cameraStatus.is_available ? 'Available' : 'Unavailable'}
              </span>
            )}
            <button
              onClick={checkCameraStatus}
              className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
              title="Refresh camera status"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">
        <div className="relative bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
          {/* Video Stream */}
          <div className="aspect-video">
            {isStreaming ? (
              <img
                ref={imgRef}
                className="w-full h-full object-cover"
                onError={handleImageError}
                onLoad={handleImageLoad}
                alt={`Camera ${cameraId} feed`}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-center">
                  <Camera className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400 mb-4">
                    Camera feed not active
                  </p>
                  {error && (
                    <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-4">
                      <div className="flex items-center">
                        <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400 mr-2" />
                        <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                      </div>
                    </div>
                  )}
                  <button
                    onClick={startStream}
                    disabled={isLoading}
                    className="btn-primary flex items-center mx-auto"
                  >
                    {isLoading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                    ) : (
                      <Camera className="h-4 w-4 mr-2" />
                    )}
                    Start Stream
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Stream Controls Overlay */}
          {isStreaming && (
            <div className="absolute top-2 right-2 flex space-x-2">
              <button
                onClick={stopStream}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
              >
                Stop
              </button>
              <button
                onClick={() => {/* Implement fullscreen */}}
                className="bg-black/50 hover:bg-black/70 text-white p-1 rounded transition-colors duration-200"
                title="Fullscreen"
              >
                <Maximize2 className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Stream Info Overlay */}
          {isStreaming && cameraStatus && (
            <div className="absolute bottom-2 left-2 bg-black/50 text-white px-2 py-1 rounded text-xs">
              Camera {cameraId} • Active Streams: {cameraStatus.active_streams}/{cameraStatus.max_streams}
            </div>
          )}
        </div>

        {/* Stream Information */}
        {cameraStatus && (
          <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex justify-between">
              <span>Status:</span>
              <span className={cameraStatus.is_available ? 'text-green-600' : 'text-red-600'}>
                {cameraStatus.is_available ? 'Available' : 'Unavailable'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Active Streams:</span>
              <span>{cameraStatus.active_streams} / {cameraStatus.max_streams}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CameraFeed;