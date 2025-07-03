import React, { useState, useRef, useCallback } from "react";
import { X, Camera, RotateCcw, Check, AlertCircle } from "lucide-react";
import Webcam from "react-webcam";
import Button from "../common/Button";
import Modal from "../common/Modal";

const FaceRecognitionModal = ({ isOpen, onClose, onSuccess, sessionId }) => {
  const webcamRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState("");
  const [step, setStep] = useState("capture"); // capture, confirm, processing

  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: "user",
  };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImageeSrc(imageSrc);
    setStep("confirm");
    setError("");
  }, [webcamRef]);

  const retake = () => {
    setImageSrc(null);
    setStep("capture");
    setError("");
  };

  const submitAttendance = async () => {
    if (!imageSrc) {
      setError("No image captured");
      return;
    }

    setIsProcessing(true);
    setStep("processing");
    setError("");

    try {
      // Convert base64 to blob
      const response = await fetch(imageSrc);
      const blob = await response.blob();

      // Create form data
      const formData = new FormData();
      formData.append("image", blob, "attendance-photo.jpg");

      // Submit to API
      const result = await fetch(`/api/attendance/mark/${sessionId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("attendance_token")}`,
        },
        body: formData,
      });

      const data = await result.json();

      if (result.ok) {
        onSuccess(data);
      } else {
        throw new Error(data.detail || "Attendance marking failed");
      }
    } catch (error) {
      console.error("Attendance error:", error);
      setError(error.message);
      setStep("capture");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    setImageSrc(null);
    setStep("capture");
    setError("");
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Mark Attendance"
      size="large"
    >
      <div className="space-y-6">
        {/* Instructions */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Camera className="h-5 w-5 text-blue-400 mt-0.5" />
            <div>
              <p className="text-blue-400 font-medium mb-1">
                Face Recognition Instructions
              </p>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• Position your face clearly in the camera frame</li>
                <li>• Ensure good lighting on your face</li>
                <li>• Look directly at the camera</li>
                <li>• Remove glasses if possible for better recognition</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <p className="text-red-400 font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Camera/Image Display */}
        <div className="relative bg-gray-800 rounded-lg overflow-hidden">
          {step === "capture" && (
            <div className="relative">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={videoConstraints}
                className="w-full h-auto"
              />

              {/* Face detection overlay */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-64 h-64 border-2 border-blue-400 rounded-full opacity-50">
                  <div className="w-full h-full border-2 border-blue-400 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>
          )}

          {step === "confirm" && imageSrc && (
            <div className="relative">
              <img src={imageSrc} alt="Captured" className="w-full h-auto" />
              <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm">
                Image Captured
              </div>
            </div>
          )}

          {step === "processing" && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
                <p className="text-white font-medium">
                  Processing face recognition...
                </p>
                <p className="text-gray-400 text-sm">
                  This may take a few seconds
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between">
          {step === "capture" && (
            <>
              <Button onClick={handleClose} variant="secondary">
                Cancel
              </Button>
              <Button
                onClick={capture}
                variant="primary"
                className="flex items-center gap-2"
              >
                <Camera className="h-4 w-4" />
                Capture Photo
              </Button>
            </>
          )}

          {step === "confirm" && (
            <>
              <Button
                onClick={retake}
                variant="secondary"
                className="flex items-center gap-2"
              >
                <RotateCcw className="h-4 w-4" />
                Retake
              </Button>
              <Button
                onClick={submitAttendance}
                variant="success"
                className="flex items-center gap-2"
              >
                <Check className="h-4 w-4" />
                Mark Attendance
              </Button>
            </>
          )}

          {step === "processing" && (
            <Button disabled variant="secondary" className="mx-auto">
              Processing...
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default FaceRecognitionModal;
