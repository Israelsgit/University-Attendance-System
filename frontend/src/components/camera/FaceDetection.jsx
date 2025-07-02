import React, { useRef, useEffect, useState } from "react";
import { Scan, User, CheckCircle, AlertCircle } from "lucide-react";

const FaceDetection = ({
  isActive = false,
  onFaceDetected,
  onFaceLost,
  confidence = 0.8,
}) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);

  const [detectionState, setDetectionState] = useState({
    faceDetected: false,
    confidence: 0,
    boundingBox: null,
    processing: false,
  });

  useEffect(() => {
    if (isActive) {
      startDetection();
    } else {
      stopDetection();
    }

    return () => stopDetection();
  }, [isActive]);

  const startDetection = () => {
    if (intervalRef.current) return;

    intervalRef.current = setInterval(() => {
      detectFace();
    }, 100); // Check every 100ms for smooth detection
  };

  const stopDetection = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const detectFace = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    try {
      setDetectionState((prev) => ({ ...prev, processing: true }));

      // Simulate face detection (in real implementation, this would use actual ML models)
      const mockDetection = await simulateFaceDetection();

      setDetectionState((prev) => ({
        ...prev,
        faceDetected: mockDetection.detected,
        confidence: mockDetection.confidence,
        boundingBox: mockDetection.boundingBox,
        processing: false,
      }));

      // Trigger callbacks
      if (mockDetection.detected && mockDetection.confidence >= confidence) {
        onFaceDetected &&
          onFaceDetected({
            confidence: mockDetection.confidence,
            boundingBox: mockDetection.boundingBox,
            timestamp: Date.now(),
          });
      } else if (!mockDetection.detected && detectionState.faceDetected) {
        onFaceLost && onFaceLost();
      }
    } catch (error) {
      console.error("Face detection error:", error);
      setDetectionState((prev) => ({ ...prev, processing: false }));
    }
  };

  const simulateFaceDetection = () => {
    return new Promise((resolve) => {
      // Simulate processing time
      setTimeout(() => {
        // Mock face detection result (85% chance of detection with random confidence)
        const detected = Math.random() > 0.15;
        const mockConfidence = detected
          ? 0.7 + Math.random() * 0.3
          : Math.random() * 0.4;

        resolve({
          detected,
          confidence: mockConfidence,
          boundingBox: detected
            ? {
                x: 160 + Math.random() * 40,
                y: 120 + Math.random() * 40,
                width: 200 + Math.random() * 50,
                height: 240 + Math.random() * 60,
              }
            : null,
        });
      }, 50 + Math.random() * 100);
    });
  };

  const drawDetectionOverlay = () => {
    if (!canvasRef.current || !videoRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext("2d");

    // Set canvas size to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (detectionState.faceDetected && detectionState.boundingBox) {
      const { x, y, width, height } = detectionState.boundingBox;
      const color =
        detectionState.confidence >= confidence ? "#10B981" : "#F59E0B";

      // Draw bounding box
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, width, height);

      // Draw confidence score
      ctx.fillStyle = color;
      ctx.font = "16px Inter, sans-serif";
      ctx.fillText(
        `${Math.round(detectionState.confidence * 100)}%`,
        x,
        y - 10
      );

      // Draw corner indicators
      const cornerSize = 20;
      ctx.lineWidth = 4;

      // Top-left corner
      ctx.beginPath();
      ctx.moveTo(x, y + cornerSize);
      ctx.lineTo(x, y);
      ctx.lineTo(x + cornerSize, y);
      ctx.stroke();

      // Top-right corner
      ctx.beginPath();
      ctx.moveTo(x + width - cornerSize, y);
      ctx.lineTo(x + width, y);
      ctx.lineTo(x + width, y + cornerSize);
      ctx.stroke();

      // Bottom-left corner
      ctx.beginPath();
      ctx.moveTo(x, y + height - cornerSize);
      ctx.lineTo(x, y + height);
      ctx.lineTo(x + cornerSize, y + height);
      ctx.stroke();

      // Bottom-right corner
      ctx.beginPath();
      ctx.moveTo(x + width - cornerSize, y + height);
      ctx.lineTo(x + width, y + height);
      ctx.lineTo(x + width, y + height - cornerSize);
      ctx.stroke();
    }
  };

  // Update overlay when detection state changes
  useEffect(() => {
    drawDetectionOverlay();
  }, [detectionState]);

  return (
    <div className="relative">
      {/* Detection overlay canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 z-10 pointer-events-none"
        style={{
          width: "100%",
          height: "100%",
        }}
      />

      {/* Detection status indicator */}
      {isActive && (
        <div className="absolute top-4 left-4 z-20">
          <div
            className={`
            flex items-center px-3 py-2 rounded-lg border backdrop-blur-sm
            ${
              detectionState.faceDetected
                ? detectionState.confidence >= confidence
                  ? "bg-green-500/20 border-green-500/40 text-green-300"
                  : "bg-yellow-500/20 border-yellow-500/40 text-yellow-300"
                : "bg-red-500/20 border-red-500/40 text-red-300"
            }
          `}
          >
            {detectionState.processing ? (
              <Scan className="h-4 w-4 mr-2 animate-spin" />
            ) : detectionState.faceDetected ? (
              detectionState.confidence >= confidence ? (
                <CheckCircle className="h-4 w-4 mr-2" />
              ) : (
                <AlertCircle className="h-4 w-4 mr-2" />
              )
            ) : (
              <User className="h-4 w-4 mr-2" />
            )}

            <span className="text-sm font-medium">
              {detectionState.processing
                ? "Scanning..."
                : detectionState.faceDetected
                ? detectionState.confidence >= confidence
                  ? "Face Detected"
                  : "Low Confidence"
                : "No Face"}
            </span>

            {detectionState.faceDetected && (
              <span className="ml-2 text-xs opacity-75">
                {Math.round(detectionState.confidence * 100)}%
              </span>
            )}
          </div>
        </div>
      )}

      {/* Center crosshair for face positioning */}
      {isActive && !detectionState.faceDetected && (
        <div className="absolute inset-0 z-10 flex items-center justify-center pointer-events-none">
          <div className="relative">
            {/* Outer circle */}
            <div className="w-64 h-64 rounded-full border-2 border-white/30 border-dashed animate-pulse">
              {/* Inner circle */}
              <div className="absolute inset-4 rounded-full border border-white/50">
                {/* Center dot */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-white/70 rounded-full"></div>
              </div>
            </div>

            {/* Guidelines */}
            <div className="absolute top-1/2 left-0 w-full h-px bg-white/20 transform -translate-y-1/2"></div>
            <div className="absolute top-0 left-1/2 w-px h-full bg-white/20 transform -translate-x-1/2"></div>
          </div>

          {/* Instruction text */}
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-center">
            <p className="text-white/80 text-sm">
              Position your face in the center
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FaceDetection;
