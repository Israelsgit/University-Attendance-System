import React, { useRef, useEffect, useState } from "react";
import { Camera, X, CheckCircle, AlertCircle, Scan } from "lucide-react";
import Button from "../common/Button";
import Modal from "../common/Modal";

const CameraCapture = ({
  onCapture,
  onClose,
  isProcessing = false,
  mode = "check-in",
}) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);

  useEffect(() => {
    initializeCamera();

    return () => {
      stopCamera();
    };
  }, []);

  const initializeCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user",
        },
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          setIsInitialized(true);
        };
      }
    } catch (err) {
      console.error("Camera initialization error:", err);
      setError("Unable to access camera. Please check permissions.");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
    }
  };

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return null;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/jpeg", 0.8);
  };

  const handleCapture = async () => {
    setIsDetecting(true);
    setDetectionResult(null);

    try {
      const imageData = captureFrame();
      if (!imageData) {
        throw new Error("Failed to capture image");
      }

      // Simulate face detection processing
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Mock face detection result
      const mockResult = {
        faceDetected: true,
        confidence: 0.95,
        userId: "user_123",
        timestamp: new Date().toISOString(),
      };

      setDetectionResult(mockResult);

      if (mockResult.faceDetected && mockResult.confidence > 0.8) {
        // Success - call the onCapture callback
        setTimeout(() => {
          onCapture({
            imageData,
            faceData: mockResult,
            mode,
          });
        }, 1500);
      } else {
        setError("Face not detected or confidence too low. Please try again.");
      }
    } catch (err) {
      console.error("Face detection error:", err);
      setError("Face detection failed. Please try again.");
    } finally {
      setIsDetecting(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setDetectionResult(null);
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={`Face Recognition - ${
        mode === "check-in" ? "Check In" : "Check Out"
      }`}
      maxWidth="2xl"
      closeOnOverlayClick={false}
    >
      <div className="space-y-6">
        {/* Instructions */}
        <div className="text-center p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
          <Scan className="h-8 w-8 text-blue-400 mx-auto mb-2" />
          <p className="text-blue-300 text-sm">
            Position your face in the center of the frame and click capture when
            ready
          </p>
        </div>

        {/* Camera View */}
        <div className="relative bg-black rounded-lg overflow-hidden">
          {!isInitialized && !error && (
            <div className="aspect-video flex items-center justify-center">
              <div className="text-center">
                <Camera className="h-12 w-12 text-gray-400 mx-auto mb-2 animate-pulse" />
                <p className="text-gray-400">Initializing camera...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="aspect-video flex items-center justify-center">
              <div className="text-center">
                <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-2" />
                <p className="text-red-400 mb-4">{error}</p>
                <Button
                  onClick={initializeCamera}
                  variant="primary"
                  size="small"
                >
                  Retry Camera
                </Button>
              </div>
            </div>
          )}

          {isInitialized && !error && (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full aspect-video object-cover"
              />

              {/* Face detection overlay */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div
                  className={`
                  w-64 h-64 border-2 rounded-full transition-all duration-300
                  ${
                    isDetecting
                      ? "border-yellow-400 animate-pulse"
                      : detectionResult?.faceDetected
                      ? "border-green-400"
                      : "border-white/50"
                  }
                `}
                >
                  <div className="w-full h-full rounded-full border-2 border-white/20"></div>
                </div>
              </div>

              {/* Detection status */}
              {isDetecting && (
                <div className="absolute top-4 left-4 right-4">
                  <div className="bg-yellow-500/20 border border-yellow-500/40 rounded-lg p-3">
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-yellow-400 border-t-transparent mr-3"></div>
                      <span className="text-yellow-300 text-sm">
                        Detecting face...
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {detectionResult && (
                <div className="absolute top-4 left-4 right-4">
                  <div
                    className={`
                    rounded-lg p-3 border
                    ${
                      detectionResult.faceDetected
                        ? "bg-green-500/20 border-green-500/40"
                        : "bg-red-500/20 border-red-500/40"
                    }
                  `}
                  >
                    <div className="flex items-center">
                      {detectionResult.faceDetected ? (
                        <CheckCircle className="h-4 w-4 text-green-400 mr-3" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-400 mr-3" />
                      )}
                      <div>
                        <span
                          className={`text-sm ${
                            detectionResult.faceDetected
                              ? "text-green-300"
                              : "text-red-300"
                          }`}
                        >
                          {detectionResult.faceDetected
                            ? `Face detected (${Math.round(
                                detectionResult.confidence * 100
                              )}% confidence)`
                            : "No face detected"}
                        </span>
                        {detectionResult.faceDetected && (
                          <p className="text-xs text-green-400 mt-1">
                            {mode === "check-in"
                              ? "Checking you in..."
                              : "Checking you out..."}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Hidden canvas for image capture */}
        <canvas ref={canvasRef} className="hidden" />

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          {!detectionResult?.faceDetected && (
            <>
              <Button
                onClick={onClose}
                variant="secondary"
                disabled={isDetecting || isProcessing}
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>

              <Button
                onClick={error ? handleRetry : handleCapture}
                variant="primary"
                disabled={!isInitialized || isDetecting || isProcessing}
                loading={isDetecting}
              >
                <Camera className="h-4 w-4 mr-2" />
                {error ? "Try Again" : isDetecting ? "Detecting..." : "Capture"}
              </Button>
            </>
          )}
        </div>

        {/* Processing Status */}
        {isProcessing && (
          <div className="text-center p-4 bg-primary-500/10 rounded-lg border border-primary-500/20">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary-400 border-t-transparent mx-auto mb-2"></div>
            <p className="text-primary-300 text-sm">
              Processing {mode === "check-in" ? "check-in" : "check-out"}...
            </p>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default CameraCapture;
