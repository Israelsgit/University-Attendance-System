import axios from "axios";
import toast from "react-hot-toast";

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000/api",
  timeout: 30000, // 30 seconds
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false, // Set to true if you need cookies
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log request for debugging
    console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, {
      data: config.data,
      headers: config.headers,
    });

    return config;
  },
  (error) => {
    console.error("❌ Request interceptor error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor for handling responses and errors
apiClient.interceptors.response.use(
  (response) => {
    // Log successful response
    console.log(`✅ ${response.status} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    // Log error for debugging
    console.error("❌ API Error:", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });

    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          toast.error("Session expired. Please login again.");
          if (window.location.pathname !== "/login") {
            window.location.href = "/login";
          }
          break;

        case 403:
          toast.error("Access denied. Insufficient permissions.");
          break;

        case 404:
          toast.error("Resource not found.");
          break;

        case 422:
          // Validation errors
          if (data.detail && Array.isArray(data.detail)) {
            const errorMessages = data.detail.map((err) => err.msg).join(", ");
            toast.error(`Validation error: ${errorMessages}`);
          } else {
            toast.error(data.message || "Validation error occurred.");
          }
          break;

        case 500:
          toast.error("Server error. Please try again later.");
          break;

        default:
          toast.error(data?.message || `Error ${status}: ${error.message}`);
      }

      // Return formatted error
      return Promise.reject({
        status,
        message: data?.message || error.message,
        errors: data?.errors || null,
        data: data,
      });
    } else if (error.request) {
      // Network error
      console.error("🌐 Network Error:", error.request);
      toast.error("Network error. Please check your connection.");
      return Promise.reject({
        status: 0,
        message: "Network error. Please check your connection.",
        errors: null,
        data: null,
      });
    } else {
      // Other error
      console.error("❌ Unknown Error:", error.message);
      toast.error("An unexpected error occurred.");
      return Promise.reject({
        status: 0,
        message: error.message,
        errors: null,
        data: null,
      });
    }
  }
);

// Test API connection
export const testConnection = async () => {
  try {
    const response = await apiClient.get("/health");
    console.log("✅ API connection successful:", response.data);
    return { success: true, data: response.data };
  } catch (error) {
    console.error("❌ API connection failed:", error);
    return {
      success: false,
      error: error.message || "Connection failed",
    };
  }
};

export default apiClient;
