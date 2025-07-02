import { useState, useRef, useEffect, useCallback } from "react";

export const useCamera = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stream, setStream] = useState(null);
  const [devices, setDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState(null);

  const videoRef = useRef(null);

  // Initialize camera
  const initializeCamera = useCallback(
    async (constraints = {}) => {
      try {
        setIsLoading(true);
        setError(null);

        const defaultConstraints = {
          video: {
            width: { ideal: 1280, max: 1920 },
            height: { ideal: 720, max: 1080 },
            facingMode: "user",
            frameRate: { ideal: 30, max: 60 },
            ...constraints.video,
          },
          audio: false,
          ...constraints,
        };

        // If a specific device is selected, use it
        if (selectedDeviceId) {
          defaultConstraints.video.deviceId = { exact: selectedDeviceId };
        }

        const mediaStream = await navigator.mediaDevices.getUserMedia(
          defaultConstraints
        );

        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          videoRef.current.onloadedmetadata = () => {
            setIsInitialized(true);
            setIsLoading(false);
          };
        }

        setStream(mediaStream);
        return mediaStream;
      } catch (err) {
        console.error("Camera initialization error:", err);

        let errorMessage = "Unable to access camera";

        if (err.name === "NotAllowedError") {
          errorMessage =
            "Camera access denied. Please allow camera permissions.";
        } else if (err.name === "NotFoundError") {
          errorMessage = "No camera found on this device.";
        } else if (err.name === "NotReadableError") {
          errorMessage = "Camera is already in use by another application.";
        } else if (err.name === "OverconstrainedError") {
          errorMessage = "Camera constraints not supported.";
        }

        setError(errorMessage);
        setIsLoading(false);
        throw new Error(errorMessage);
      }
    },
    [selectedDeviceId]
  );

  // Get available camera devices
  const getDevices = useCallback(async () => {
    try {
      const deviceList = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = deviceList.filter(
        (device) => device.kind === "videoinput"
      );
      setDevices(videoDevices);

      // Auto-select the first device if none selected
      if (videoDevices.length > 0 && !selectedDeviceId) {
        setSelectedDeviceId(videoDevices[0].deviceId);
      }

      return videoDevices;
    } catch (err) {
      console.error("Error getting devices:", err);
      setError("Unable to get camera devices");
      return [];
    }
  }, [selectedDeviceId]);

  // Stop camera
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach((track) => {
        track.stop();
      });
      setStream(null);
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setIsInitialized(false);
  }, [stream]);

  // Switch camera device
  const switchDevice = useCallback(
    async (deviceId) => {
      stopCamera();
      setSelectedDeviceId(deviceId);
      await initializeCamera();
    },
    [stopCamera, initializeCamera]
  );

  // Capture photo from video stream
  const capturePhoto = useCallback(
    (quality = 0.8) => {
      if (!videoRef.current || !isInitialized) {
        throw new Error("Camera not initialized");
      }

      const video = videoRef.current;
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      return canvas.toDataURL("image/jpeg", quality);
    },
    [isInitialized]
  );

  // Capture blob for file upload
  const captureBlob = useCallback(
    (quality = 0.8) => {
      return new Promise((resolve, reject) => {
        if (!videoRef.current || !isInitialized) {
          reject(new Error("Camera not initialized"));
          return;
        }

        const video = videoRef.current;
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(resolve, "image/jpeg", quality);
      });
    },
    [isInitialized]
  );

  // Check camera permissions
  const checkPermissions = useCallback(async () => {
    try {
      const permissions = await navigator.permissions.query({ name: "camera" });
      return permissions.state;
    } catch (err) {
      console.error("Error checking permissions:", err);
      return "unknown";
    }
  }, []);

  // Request camera permissions
  const requestPermissions = useCallback(async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ video: true });
      return true;
    } catch (err) {
      console.error("Permission request failed:", err);
      return false;
    }
  }, []);

  // Get video track settings
  const getVideoSettings = useCallback(() => {
    if (!stream) return null;

    const videoTrack = stream.getVideoTracks()[0];
    if (!videoTrack) return null;

    return {
      settings: videoTrack.getSettings(),
      capabilities: videoTrack.getCapabilities(),
      constraints: videoTrack.getConstraints(),
    };
  }, [stream]);

  // Apply video constraints
  const applyConstraints = useCallback(
    async (constraints) => {
      if (!stream) {
        throw new Error("No active stream");
      }

      const videoTrack = stream.getVideoTracks()[0];
      if (!videoTrack) {
        throw new Error("No video track available");
      }

      try {
        await videoTrack.applyConstraints(constraints);
        return true;
      } catch (err) {
        console.error("Error applying constraints:", err);
        throw err;
      }
    },
    [stream]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  // Initialize devices list on mount
  useEffect(() => {
    getDevices();
  }, [getDevices]);

  return {
    // State
    isInitialized,
    isLoading,
    error,
    stream,
    devices,
    selectedDeviceId,
    videoRef,

    // Actions
    initializeCamera,
    stopCamera,
    switchDevice,
    capturePhoto,
    captureBlob,
    getDevices,
    checkPermissions,
    requestPermissions,
    getVideoSettings,
    applyConstraints,

    // Utilities
    setSelectedDeviceId,
    setError: (error) => setError(error),
  };
};
