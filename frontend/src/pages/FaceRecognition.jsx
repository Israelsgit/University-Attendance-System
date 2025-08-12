import React, { useState, useRef, useCallback, useEffect } from "react";
import {
  Camera,
  UserCheck,
  X,
  RotateCcw,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { toast } from "react-hot-toast";

import { useAuth } from "../hooks/useAuth";
import { authAPI } from "../services/apiClient";
import Button from "../components/common/Button";
import LoadingSpinner from "../components/common/LoadingSpinner";

const FaceRecognition = () => {
  const { user } = useAuth();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [isStreaming, setIsStreaming] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [mode, setMode] = useState("register"); // "register" or "verify"
  const [verificationResult, setVerificationResult] = useState(null);

  useEffect(() => {
    // Cleanup camera when component unmounts
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = useCallback(async () => {
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
        setIsStreaming(true);
      }
    } catch (error) {
      console.error("Error accessing camera:", error);
      toast.error("Could not access camera. Please check permissions.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      setIsStreaming(false);
    }
  }, []);

  const captureImage = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const context = canvas.getContext("2d");
      context.drawImage(video, 0, 0);

      // Convert to base64
      const imageData = canvas.toDataURL("image/jpeg", 0.8);
      setCapturedImage(imageData);
      stopCamera();
    }
  }, [stopCamera]);

  const retakePhoto = useCallback(() => {
    setCapturedImage(null);
    setVerificationResult(null);
    startCamera();
  }, [startCamera]);

  const registerFace = async () => {
    if (!capturedImage) return;

    setIsProcessing(true);

    try {
      const response = await authAPI.registerFace({
        image_data: capturedImage,
        confidence_threshold: 0.8,
      });

      if (response.data.is_face_registered) {
        toast.success("Face registered successfully!");
        setCapturedImage(null);
        // Refresh user data if needed
      } else {
        toast.error("Face registration failed. Please try again.");
      }
    } catch (error) {
      console.error("Face registration error:", error);
      toast.error(error.response?.data?.detail || "Face registration failed");
    } finally {
      setIsProcessing(false);
    }
  };

  const verifyFace = async () => {
    if (!capturedImage) return;

    setIsProcessing(true);

    try {
      const response = await authAPI.verifyFace({
        image_data: capturedImage,
      });

      setVerificationResult(response.data);

      if (response.data.verified) {
        toast.success("Face verified successfully!");
      } else {
        toast.error("Face verification failed. Please try again.");
      }
    } catch (error) {
      console.error("Face verification error:", error);
      toast.error(error.response?.data?.detail || "Face verification failed");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleProcess = () => {
    if (mode === "register") {
      registerFace();
    } else {
      verifyFace();
    }
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Face Recognition
          </h1>
          <p className="text-gray-400">
            {mode === "register"
              ? "Register your face for automatic attendance marking"
              : "Verify your identity for attendance"}
          </p>
        </div>

        {/* Mode Selection */}
        <div className="mb-6">
          <div className="flex gap-4">
            <Button
              onClick={() => {
                setMode("register");
                setCapturedImage(null);
                setVerificationResult(null);
                stopCamera();
              }}
              variant={mode === "register" ? "primary" : "secondary"}
            >
              <UserCheck className="h-4 w-4 mr-2" />
              Register Face
            </Button>
            <Button
              onClick={() => {
                setMode("verify");
                setCapturedImage(null);
                setVerificationResult(null);
                stopCamera();
              }}
              variant={mode === "verify" ? "primary" : "secondary"}
            >
              <Camera className="h-4 w-4 mr-2" />
              Verify Face
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Camera Section */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Camera</h2>

            <div className="space-y-4">
              {/* Camera View */}
              <div className="relative bg-gray-900 rounded-lg overflow-hidden">
                {isStreaming ? (
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    className="w-full h-64 object-cover"
                  />
                ) : capturedImage ? (
                  <img
                    src={capturedImage}
                    alt="Captured face"
                    className="w-full h-64 object-cover"
                  />
                ) : (
                  <div className="w-full h-64 flex items-center justify-center">
                    <div className="text-center">
                      <Camera className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                      <p className="text-gray-400">Camera not active</p>
                    </div>
                  </div>
                )}

                {/* Face detection overlay */}
                {isStreaming && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-48 h-64 border-2 border-blue-400 rounded-lg border-dashed opacity-50"></div>
                  </div>
                )}
              </div>

              {/* Camera Controls */}
              <div className="flex gap-3">
                {!isStreaming && !capturedImage && (
                  <Button
                    onClick={startCamera}
                    variant="primary"
                    className="flex-1"
                  >
                    <Camera className="h-4 w-4 mr-2" />
                    Start Camera
                  </Button>
                )}

                {isStreaming && (
                  <Button
                    onClick={captureImage}
                    variant="primary"
                    className="flex-1"
                  >
                    <Camera className="h-4 w-4 mr-2" />
                    Capture
                  </Button>
                )}

                {capturedImage && (
                  <Button
                    onClick={retakePhoto}
                    variant="secondary"
                    className="flex-1"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Retake
                  </Button>
                )}

                {isStreaming && (
                  <Button onClick={stopCamera} variant="secondary">
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Process Section */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              {mode === "register" ? "Face Registration" : "Face Verification"}
            </h2>

            <div className="space-y-4">
              {/* Instructions */}
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <h3 className="text-blue-400 font-medium mb-2">
                  Instructions:
                </h3>
                <ul className="text-blue-300 text-sm space-y-1">
                  <li>• Look directly at the camera</li>
                  <li>• Ensure good lighting on your face</li>
                  <li>• Remove glasses if possible</li>
                  <li>• Keep a neutral expression</li>
                  <li>• Stay still during capture</li>
                </ul>
              </div>

              {/* User Info */}
              {user && (
                <div className="bg-gray-500/10 border border-gray-500/20 rounded-lg p-4">
                  <h3 className="text-white font-medium mb-2">
                    User Information:
                  </h3>
                  <p className="text-gray-300 text-sm">{user.full_name}</p>
                  <p className="text-gray-400 text-xs">{user.email}</p>
                  {user.role === "student" && user.matric_number && (
                    <p className="text-gray-500 text-xs">
                      {user.matric_number}
                    </p>
                  )}
                  {user.role === "lecturer" && user.staff_id && (
                    <p className="text-gray-500 text-xs">{user.staff_id}</p>
                  )}
                </div>
              )}

              {/* Process Button */}
              {capturedImage && (
                <Button
                  onClick={handleProcess}
                  variant="primary"
                  loading={isProcessing}
                  className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <LoadingSpinner size="small" className="mr-2" />
                      {mode === "register" ? "Registering..." : "Verifying..."}
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      {mode === "register" ? "Register Face" : "Verify Face"}
                    </>
                  )}
                </Button>
              )}

              {/* Verification Result */}
              {verificationResult && mode === "verify" && (
                <div
                  className={`rounded-lg p-4 border ${
                    verificationResult.verified
                      ? "bg-green-500/10 border-green-500/20"
                      : "bg-red-500/10 border-red-500/20"
                  }`}
                >
                  <div className="flex items-center">
                    {verificationResult.verified ? (
                      <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                    )}
                    <div>
                      <p
                        className={`font-medium ${
                          verificationResult.verified
                            ? "text-green-400"
                            : "text-red-400"
                        }`}
                      >
                        {verificationResult.verified
                          ? "Verification Successful"
                          : "Verification Failed"}
                      </p>
                      {verificationResult.confidence && (
                        <p className="text-sm text-gray-400">
                          Confidence:{" "}
                          {(verificationResult.confidence * 100).toFixed(1)}%
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Current Status */}
              {user && (
                <div className="bg-gray-500/10 border border-gray-500/20 rounded-lg p-4">
                  <h3 className="text-white font-medium mb-2">
                    Current Status:
                  </h3>
                  <div className="flex items-center">
                    {user.is_face_registered ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                        <span className="text-green-400 text-sm">
                          Face Registered
                        </span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-4 w-4 text-yellow-400 mr-2" />
                        <span className="text-yellow-400 text-sm">
                          Face Not Registered
                        </span>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Hidden canvas for image processing */}
        <canvas ref={canvasRef} className="hidden" />
      </div>
    </div>
  );
};

export default FaceRecognition;
