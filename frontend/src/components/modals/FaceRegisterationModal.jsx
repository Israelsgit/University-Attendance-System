import React, { useState, useRef, useCallback } from "react";
import { Camera, X, CheckCircle, AlertTriangle, RotateCcw } from "lucide-react";
import Button from "../common/Button";
import { authAPI } from "../../services/apiClient";
import { toast } from "react-hot-toast";

const FaceRegistrationModal = ({ isOpen, onClose, onSuccess }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [step, setStep] = useState(1); // 1: instructions, 2: camera, 3: captured, 4: processing, 5: success

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
        setStep(2);
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
      setStep(3);
      stopCamera();
    }
  }, [stopCamera]);

  const retakePhoto = useCallback(() => {
    setCapturedImage(null);
    setStep(1);
  }, []);

  const registerFace = async () => {
    if (!capturedImage) return;

    setIsProcessing(true);
    setStep(4);

    try {
      const response = await authAPI.registerFace({
        image_data: capturedImage,
        confidence_threshold: 0.8,
      });

      if (response.data.is_face_registered) {
        setStep(5);
        setTimeout(() => {
          onSuccess();
        }, 2000);
      } else {
        toast.error("Face registration failed. Please try again.");
        setStep(3);
      }
    } catch (error) {
      console.error("Face registration error:", error);
      toast.error(error.response?.data?.detail || "Face registration failed");
      setStep(3);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    stopCamera();
    setCapturedImage(null);
    setStep(1);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">
            Face Registration
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Step 1: Instructions */}
          {step === 1 && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto">
                <Camera className="h-8 w-8 text-blue-400" />
              </div>

              <div>
                <h3 className="text-lg font-medium text-white mb-2">
                  Register Your Face
                </h3>
                <p className="text-gray-400 text-sm">
                  We'll capture your face to enable automatic attendance
                  marking. Please follow these guidelines:
                </p>
              </div>

              <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 text-left">
                <div className="flex items-start">
                  <AlertTriangle className="h-5 w-5 text-amber-400 mt-0.5 mr-3 flex-shrink-0" />
                  <div className="text-sm">
                    <p className="text-amber-400 font-medium mb-2">
                      Important Tips:
                    </p>
                    <ul className="text-amber-300 space-y-1">
                      <li>• Look directly at the camera</li>
                      <li>• Ensure good lighting on your face</li>
                      <li>• Remove glasses if possible</li>
                      <li>• Keep a neutral expression</li>
                      <li>• Stay still during capture</li>
                    </ul>
                  </div>
                </div>
              </div>

              <Button
                onClick={startCamera}
                variant="primary"
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                <Camera className="h-4 w-4 mr-2" />
                Start Camera
              </Button>
            </div>
          )}

          {/* Step 2: Camera View */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="relative">
                <video
                  ref={videoRef}
                  autoPlay
                  muted
                  className="w-full h-64 bg-gray-900 rounded-lg object-cover"
                />
                {/* Face detection overlay */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-48 h-64 border-2 border-blue-400 rounded-lg border-dashed opacity-50"></div>
                </div>
              </div>

              <p className="text-center text-gray-400 text-sm">
                Position your face within the outline and click capture
              </p>

              <div className="flex gap-3">
                <Button
                  onClick={retakePhoto}
                  variant="secondary"
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={captureImage}
                  variant="primary"
                  className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                >
                  <Camera className="h-4 w-4 mr-2" />
                  Capture
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Captured Image Review */}
          {step === 3 && capturedImage && (
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-medium text-white mb-2">
                  Review Your Photo
                </h3>
                <p className="text-gray-400 text-sm">
                  Make sure your face is clearly visible and well-lit
                </p>
              </div>

              <div className="relative">
                <img
                  src={capturedImage}
                  alt="Captured face"
                  className="w-full h-64 bg-gray-900 rounded-lg object-cover"
                />
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={retakePhoto}
                  variant="secondary"
                  className="flex-1"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Retake
                </Button>
                <Button
                  onClick={registerFace}
                  variant="primary"
                  className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Register Face
                </Button>
              </div>
            </div>
          )}

          {/* Step 4: Processing */}
          {step === 4 && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-white mb-2">
                  Processing Your Face
                </h3>
                <p className="text-gray-400 text-sm">
                  Please wait while we register your face for attendance...
                </p>
              </div>
            </div>
          )}

          {/* Step 5: Success */}
          {step === 5 && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>

              <div>
                <h3 className="text-lg font-medium text-white mb-2">
                  Face Registered Successfully!
                </h3>
                <p className="text-gray-400 text-sm">
                  You can now mark attendance using facial recognition
                </p>
              </div>

              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <p className="text-green-400 text-sm">
                  Your face has been securely registered. You can now mark
                  attendance for your enrolled courses automatically.
                </p>
              </div>
            </div>
          )}

          {/* Hidden canvas for image processing */}
          <canvas ref={canvasRef} className="hidden" />
        </div>
      </div>
    </div>
  );
};

export default FaceRegistrationModal;
