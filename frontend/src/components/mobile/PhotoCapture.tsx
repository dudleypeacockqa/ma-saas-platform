/**
 * Photo Capture Component
 * Sprint 24: Camera integration for document scanning and photo capture
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  Box,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Fab,
  Stack,
  Card,
  CardMedia,
  CardActions,
  CircularProgress,
  Alert,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  PhotoCamera as CameraIcon,
  CameraAlt as CameraAltIcon,
  FlipCameraIos as FlipIcon,
  Flash as FlashIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Crop as CropIcon,
  DocumentScanner as ScanIcon,
  Upload as UploadIcon,
  Refresh as RetryIcon,
} from '@mui/icons-material';

export interface CapturedPhoto {
  id: string;
  dataUrl: string;
  blob: Blob;
  metadata: {
    timestamp: number;
    width: number;
    height: number;
    size: number;
    type: string;
    location?: GeolocationPosition;
  };
}

interface PhotoCaptureProps {
  onPhotoCapture?: (photo: CapturedPhoto) => void;
  onError?: (error: string) => void;
  maxPhotos?: number;
  quality?: number;
  documentMode?: boolean;
  allowMultiple?: boolean;
  autoEnhance?: boolean;
}

const PhotoCapture: React.FC<PhotoCaptureProps> = ({
  onPhotoCapture,
  onError,
  maxPhotos = 5,
  quality = 0.8,
  documentMode = false,
  allowMultiple = false,
  autoEnhance = true,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [isOpen, setIsOpen] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment');
  const [flashMode, setFlashMode] = useState<'off' | 'on' | 'auto'>('off');
  const [capturedPhotos, setCapturedPhotos] = useState<CapturedPhoto[]>([]);
  const [currentPhoto, setCurrentPhoto] = useState<CapturedPhoto | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check camera permission and capabilities
  useEffect(() => {
    checkCameraPermission();
  }, []);

  const checkCameraPermission = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('Camera not supported in this browser');
        setHasPermission(false);
        return;
      }

      const permission = await navigator.permissions.query({ name: 'camera' as PermissionName });
      setHasPermission(permission.state === 'granted');

      permission.onchange = () => {
        setHasPermission(permission.state === 'granted');
      };
    } catch (error) {
      console.error('Error checking camera permission:', error);
      setHasPermission(false);
    }
  };

  const startCamera = async () => {
    try {
      setError(null);
      setIsCapturing(true);

      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: documentMode ? 1920 : 1280 },
          height: { ideal: documentMode ? 1080 : 720 },
          aspectRatio: documentMode ? 1.77 : 1.33,
        },
        audio: false,
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }

      setHasPermission(true);
    } catch (error) {
      console.error('Error starting camera:', error);
      setError('Failed to access camera. Please check permissions.');
      setIsCapturing(false);
      setHasPermission(false);
      onError?.('Failed to access camera');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsCapturing(false);
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) {
      return;
    }

    setIsProcessing(true);

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      if (!context) {
        throw new Error('Canvas context not available');
      }

      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw current video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Apply enhancements for document mode
      if (documentMode && autoEnhance) {
        await enhanceDocumentImage(context, canvas);
      }

      // Convert to blob
      const blob = await new Promise<Blob>((resolve, reject) => {
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Failed to create blob'));
            }
          },
          'image/jpeg',
          quality
        );
      });

      // Get data URL for preview
      const dataUrl = canvas.toDataURL('image/jpeg', quality);

      // Get location if available
      let location: GeolocationPosition | undefined;
      try {
        location = await getCurrentLocation();
      } catch (error) {
        console.log('Location not available:', error);
      }

      // Create photo object
      const photo: CapturedPhoto = {
        id: `photo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        dataUrl,
        blob,
        metadata: {
          timestamp: Date.now(),
          width: canvas.width,
          height: canvas.height,
          size: blob.size,
          type: blob.type,
          location,
        },
      };

      setCurrentPhoto(photo);

      if (!allowMultiple) {
        stopCamera();
      }

      // Haptic feedback on supported devices
      if ('vibrate' in navigator) {
        navigator.vibrate(50);
      }

    } catch (error) {
      console.error('Error capturing photo:', error);
      setError('Failed to capture photo');
      onError?.('Failed to capture photo');
    } finally {
      setIsProcessing(false);
    }
  };

  const enhanceDocumentImage = async (context: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
    // Get image data
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    // Apply contrast and brightness enhancement
    const contrast = 1.2;
    const brightness = 10;

    for (let i = 0; i < data.length; i += 4) {
      // Apply contrast and brightness to RGB channels
      data[i] = Math.min(255, Math.max(0, contrast * (data[i] - 128) + 128 + brightness));     // Red
      data[i + 1] = Math.min(255, Math.max(0, contrast * (data[i + 1] - 128) + 128 + brightness)); // Green
      data[i + 2] = Math.min(255, Math.max(0, contrast * (data[i + 2] - 128) + 128 + brightness)); // Blue
      // Alpha channel remains unchanged
    }

    // Put enhanced image data back
    context.putImageData(imageData, 0, 0);
  };

  const getCurrentLocation = (): Promise<GeolocationPosition> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        resolve,
        reject,
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 300000 }
      );
    });
  };

  const confirmPhoto = () => {
    if (currentPhoto) {
      setCapturedPhotos(prev => [...prev, currentPhoto]);
      onPhotoCapture?.(currentPhoto);
      setCurrentPhoto(null);

      if (!allowMultiple || capturedPhotos.length >= maxPhotos - 1) {
        setIsOpen(false);
        stopCamera();
      }
    }
  };

  const retakePhoto = () => {
    setCurrentPhoto(null);
    if (!isCapturing) {
      startCamera();
    }
  };

  const switchCamera = () => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
    if (isCapturing) {
      stopCamera();
      setTimeout(() => startCamera(), 100);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).forEach(async (file) => {
      try {
        const dataUrl = await fileToDataUrl(file);
        const photo: CapturedPhoto = {
          id: `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          dataUrl,
          blob: file,
          metadata: {
            timestamp: Date.now(),
            width: 0, // Will be determined when image loads
            height: 0,
            size: file.size,
            type: file.type,
          },
        };

        setCapturedPhotos(prev => [...prev, photo]);
        onPhotoCapture?.(photo);
      } catch (error) {
        console.error('Error processing uploaded file:', error);
        onError?.('Failed to process uploaded file');
      }
    });

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const fileToDataUrl = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const openCamera = () => {
    setIsOpen(true);
    setCurrentPhoto(null);
    startCamera();
  };

  const closeCamera = () => {
    setIsOpen(false);
    stopCamera();
    setCurrentPhoto(null);
    setError(null);
  };

  if (!isMobile && hasPermission === false) {
    return (
      <Box>
        <Button
          variant="outlined"
          startIcon={<UploadIcon />}
          onClick={() => fileInputRef.current?.click()}
          fullWidth
        >
          Upload {documentMode ? 'Document' : 'Photo'}
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple={allowMultiple}
          style={{ display: 'none' }}
          onChange={handleFileUpload}
        />
      </Box>
    );
  }

  return (
    <>
      {/* Trigger Button */}
      <Fab
        color="primary"
        onClick={openCamera}
        sx={{
          position: 'fixed',
          bottom: 80,
          right: 16,
          zIndex: 1000,
        }}
      >
        {documentMode ? <ScanIcon /> : <CameraIcon />}
      </Fab>

      {/* Camera Dialog */}
      <Dialog
        open={isOpen}
        onClose={closeCamera}
        fullScreen={isMobile}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            bgcolor: 'black',
            color: 'white',
          },
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            {documentMode ? 'Scan Document' : 'Take Photo'}
          </Typography>
          <IconButton onClick={closeCamera} sx={{ color: 'white' }}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={{ p: 0, position: 'relative', minHeight: '60vh' }}>
          {error && (
            <Alert severity="error" sx={{ m: 2 }}>
              {error}
            </Alert>
          )}

          {currentPhoto ? (
            // Photo Preview
            <Box sx={{ position: 'relative', height: '100%' }}>
              <img
                src={currentPhoto.dataUrl}
                alt="Captured"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                }}
              />

              <Box sx={{ position: 'absolute', bottom: 16, left: 0, right: 0, textAlign: 'center' }}>
                <Stack direction="row" spacing={2} justifyContent="center">
                  <IconButton
                    onClick={retakePhoto}
                    sx={{
                      bgcolor: 'rgba(0,0,0,0.7)',
                      color: 'white',
                      '&:hover': { bgcolor: 'rgba(0,0,0,0.8)' },
                    }}
                  >
                    <RetryIcon />
                  </IconButton>
                  <IconButton
                    onClick={confirmPhoto}
                    sx={{
                      bgcolor: theme.palette.primary.main,
                      color: 'white',
                      '&:hover': { bgcolor: theme.palette.primary.dark },
                    }}
                  >
                    <CheckIcon />
                  </IconButton>
                </Stack>
              </Box>
            </Box>
          ) : (
            // Camera View
            <Box sx={{ position: 'relative', height: '100%' }}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                }}
              />

              {/* Camera overlay for document mode */}
              {documentMode && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '80%',
                    height: '60%',
                    border: '2px solid rgba(255,255,255,0.8)',
                    borderRadius: 2,
                    pointerEvents: 'none',
                  }}
                />
              )}

              {/* Camera controls */}
              <Box sx={{ position: 'absolute', top: 16, left: 16, right: 16 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Chip
                    label={documentMode ? 'Document Mode' : 'Photo Mode'}
                    sx={{ bgcolor: 'rgba(0,0,0,0.7)', color: 'white' }}
                  />

                  <Stack direction="row" spacing={1}>
                    <IconButton
                      onClick={switchCamera}
                      sx={{ bgcolor: 'rgba(0,0,0,0.7)', color: 'white' }}
                    >
                      <FlipIcon />
                    </IconButton>
                  </Stack>
                </Stack>
              </Box>

              {/* Capture button */}
              <Box sx={{ position: 'absolute', bottom: 32, left: 0, right: 0, textAlign: 'center' }}>
                <IconButton
                  onClick={capturePhoto}
                  disabled={isProcessing || !isCapturing}
                  sx={{
                    width: 80,
                    height: 80,
                    bgcolor: 'white',
                    color: theme.palette.primary.main,
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' },
                    '&:disabled': { bgcolor: 'rgba(255,255,255,0.5)' },
                  }}
                >
                  {isProcessing ? (
                    <CircularProgress size={32} />
                  ) : (
                    <CameraAltIcon sx={{ fontSize: 40 }} />
                  )}
                </IconButton>
              </Box>

              {/* Upload alternative */}
              <Box sx={{ position: 'absolute', bottom: 32, right: 16 }}>
                <IconButton
                  onClick={() => fileInputRef.current?.click()}
                  sx={{ bgcolor: 'rgba(0,0,0,0.7)', color: 'white' }}
                >
                  <UploadIcon />
                </IconButton>
              </Box>
            </Box>
          )}

          {/* Hidden canvas for photo processing */}
          <canvas
            ref={canvasRef}
            style={{ display: 'none' }}
          />

          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple={allowMultiple}
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default PhotoCapture;