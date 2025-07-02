// API Constants
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login",
    REGISTER: "/auth/register",
    LOGOUT: "/auth/logout",
    ME: "/auth/me",
    PROFILE: "/auth/profile",
    CHANGE_PASSWORD: "/auth/password",
    FORGOT_PASSWORD: "/auth/forgot-password",
    RESET_PASSWORD: "/auth/reset-password",
    VERIFY_EMAIL: "/auth/verify-email",
  },
  ATTENDANCE: {
    TODAY: "/attendance/today",
    HISTORY: "/attendance/history",
    CHECK_IN: "/attendance/check-in",
    CHECK_OUT: "/attendance/check-out",
    MANUAL_CHECK_IN: "/attendance/manual-check-in",
    MANUAL_CHECK_OUT: "/attendance/manual-check-out",
    WEEKLY_STATS: "/attendance/weekly-stats",
    MONTHLY_STATS: "/attendance/monthly-stats",
    ANALYTICS: "/attendance/analytics",
    LEAVE_REQUEST: "/attendance/leave-request",
  },
  USERS: {
    ALL: "/users",
    BY_ID: (id) => `/users/${id}`,
    STATS: (id) => `/users/${id}/stats`,
    SEARCH: "/users/search",
    BULK_UPLOAD: "/users/bulk-upload",
    EXPORT: "/users/export",
  },
};

// Application Constants
export const APP_CONFIG = {
  NAME: "AttendanceAI",
  VERSION: "1.0.0",
  DESCRIPTION: "Modern facial recognition attendance management system",
  COMPANY: "Your Company Name",
};

// Local Storage Keys
export const STORAGE_KEYS = {
  TOKEN: "attendance_token",
  USER: "attendance_user",
  PREFERENCES: "attendance_preferences",
  THEME: "attendance_theme",
};

// Date and Time Formats
export const DATE_FORMATS = {
  DISPLAY: "MMM dd, yyyy",
  INPUT: "yyyy-MM-dd",
  TIME: "HH:mm",
  DATETIME: "MMM dd, yyyy HH:mm",
  FULL: "EEEE, MMMM do, yyyy",
  API: "yyyy-MM-dd'T'HH:mm:ss.SSSxxx",
};

// Attendance Status Types
export const ATTENDANCE_STATUS = {
  PRESENT: "present",
  ABSENT: "absent",
  LATE: "late",
  EARLY_DEPARTURE: "early_departure",
  OVERTIME: "overtime",
  LEAVE: "leave",
  HOLIDAY: "holiday",
};

// Leave Types
export const LEAVE_TYPES = {
  SICK: "sick",
  VACATION: "vacation",
  PERSONAL: "personal",
  EMERGENCY: "emergency",
  MATERNITY: "maternity",
  PATERNITY: "paternity",
  BEREAVEMENT: "bereavement",
  UNPAID: "unpaid",
};

// User Roles
export const USER_ROLES = {
  ADMIN: "admin",
  HR: "hr",
  MANAGER: "manager",
  EMPLOYEE: "employee",
  GUEST: "guest",
};

// Departments
export const DEPARTMENTS = [
  "Engineering",
  "Marketing",
  "Sales",
  "Human Resources",
  "Finance",
  "Operations",
  "Information Technology",
  "Customer Support",
  "Legal",
  "Executive",
];

// Face Recognition Constants
export const FACE_RECOGNITION = {
  CONFIDENCE_THRESHOLD: 0.8,
  MAX_DETECTION_TIME: 30000, // 30 seconds
  DETECTION_INTERVAL: 100, // 100ms
  IMAGE_QUALITY: 0.8,
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  SUPPORTED_FORMATS: ["image/jpeg", "image/jpg", "image/png", "image/webp"],
};

// Camera Settings
export const CAMERA_SETTINGS = {
  DEFAULT_WIDTH: 640,
  DEFAULT_HEIGHT: 480,
  PREFERRED_WIDTH: 1280,
  PREFERRED_HEIGHT: 720,
  FRAME_RATE: 30,
  FACING_MODE: "user",
};

// Chart Colors
export const CHART_COLORS = {
  PRIMARY: "#3B82F6",
  SUCCESS: "#10B981",
  WARNING: "#F59E0B",
  DANGER: "#EF4444",
  INFO: "#06B6D4",
  PURPLE: "#8B5CF6",
  PINK: "#EC4899",
  INDIGO: "#6366F1",
};

// Validation Rules
export const VALIDATION_RULES = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^[\+]?[1-9][\d]{0,15}$/,
  PASSWORD: {
    MIN_LENGTH: 6,
    MAX_LENGTH: 128,
    REQUIRE_UPPERCASE: true,
    REQUIRE_LOWERCASE: true,
    REQUIRE_NUMBERS: true,
    REQUIRE_SPECIAL: false,
  },
  NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 50,
  },
  EMPLOYEE_ID: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 20,
    PATTERN: /^[A-Za-z0-9]+$/,
  },
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK: "Network error. Please check your connection.",
  UNAUTHORIZED: "You are not authorized to perform this action.",
  FORBIDDEN: "Access denied.",
  NOT_FOUND: "Resource not found.",
  SERVER_ERROR: "Internal server error. Please try again later.",
  VALIDATION: "Please check your input and try again.",
  CAMERA_ACCESS: "Camera access denied. Please allow camera permissions.",
  CAMERA_NOT_FOUND: "No camera found on this device.",
  CAMERA_IN_USE: "Camera is already in use by another application.",
  FACE_NOT_DETECTED:
    "No face detected. Please position your face in the frame.",
  LOW_CONFIDENCE: "Face recognition confidence too low. Please try again.",
  FILE_TOO_LARGE: "File size exceeds the maximum limit.",
  INVALID_FILE_TYPE: "Invalid file type. Please select a valid image.",
};

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN: "Successfully logged in!",
  LOGOUT: "Successfully logged out!",
  REGISTER: "Account created successfully!",
  PROFILE_UPDATED: "Profile updated successfully!",
  PASSWORD_CHANGED: "Password changed successfully!",
  CHECK_IN: "Checked in successfully!",
  CHECK_OUT: "Checked out successfully!",
  LEAVE_REQUEST: "Leave request submitted successfully!",
  DATA_EXPORTED: "Data exported successfully!",
  IMAGE_UPLOADED: "Image uploaded successfully!",
};

// Notification Types
export const NOTIFICATION_TYPES = {
  SUCCESS: "success",
  ERROR: "error",
  WARNING: "warning",
  INFO: "info",
};

// Theme Colors
export const THEME_COLORS = {
  LIGHT: {
    BACKGROUND: "#ffffff",
    SURFACE: "#f8fafc",
    PRIMARY: "#3b82f6",
    TEXT: "#1f2937",
  },
  DARK: {
    BACKGROUND: "#0f172a",
    SURFACE: "#1e293b",
    PRIMARY: "#3b82f6",
    TEXT: "#f1f5f9",
  },
};

// Breakpoints (matching Tailwind CSS)
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  "2XL": 1536,
};

// Animation Durations
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
  VERY_SLOW: 1000,
};

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
};
