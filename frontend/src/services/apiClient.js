// Updated API Services
import axios from "axios";

// Base configuration
const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api";
const ENABLE_MOCK = process.env.REACT_APP_MOCK_API === "true";

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(
      `🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`
    );
    return config;
  },
  (error) => {
    console.error("❌ Request interceptor error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(
      `❌ API Error: ${error.response?.status} ${error.config?.url}`,
      error.response?.data
    );

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  // Login
  login: async (credentials) => {
    if (ENABLE_MOCK) {
      return mockAuth.login(credentials);
    }

    const response = await apiClient.post("/auth/login", credentials);
    return response;
  },

  // Student Registration
  registerStudent: async (studentData) => {
    if (ENABLE_MOCK) {
      return mockAuth.registerStudent(studentData);
    }

    const response = await apiClient.post(
      "/auth/register/student",
      studentData
    );
    return response;
  },

  // Lecturer Registration
  registerLecturer: async (lecturerData) => {
    if (ENABLE_MOCK) {
      return mockAuth.registerLecturer(lecturerData);
    }

    const response = await apiClient.post(
      "/auth/register/lecturer",
      lecturerData
    );
    return response;
  },

  // Get current user
  getCurrentUser: async () => {
    if (ENABLE_MOCK) {
      return mockAuth.getCurrentUser();
    }

    const response = await apiClient.get("/auth/me");
    return response;
  },

  // Logout
  logout: async () => {
    if (ENABLE_MOCK) {
      return mockAuth.logout();
    }

    const response = await apiClient.post("/auth/logout");
    return response;
  },

  // Register face
  registerFace: async (faceData) => {
    if (ENABLE_MOCK) {
      return mockAuth.registerFace(faceData);
    }

    const response = await apiClient.post("/auth/register-face", faceData);
    return response;
  },

  // Verify face
  verifyFace: async (faceData) => {
    if (ENABLE_MOCK) {
      return mockAuth.verifyFace(faceData);
    }

    const response = await apiClient.post("/auth/verify-face", faceData);
    return response;
  },

  // Change password
  changePassword: async (passwordData) => {
    if (ENABLE_MOCK) {
      return mockAuth.changePassword(passwordData);
    }

    const response = await apiClient.post(
      "/auth/change-password",
      passwordData
    );
    return response;
  },

  // Get system info for registration
  getSystemInfo: async () => {
    if (ENABLE_MOCK) {
      return mockAuth.getSystemInfo();
    }

    const response = await apiClient.get("/auth/system-info");
    return response;
  },

  // Upload profile image
  uploadProfileImage: async (imageFile) => {
    if (ENABLE_MOCK) {
      return mockAuth.uploadProfileImage(imageFile);
    }

    const formData = new FormData();
    formData.append("file", imageFile);

    const response = await apiClient.post(
      "/auth/upload-profile-image",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response;
  },
};

// Course Management API
export const courseAPI = {
  // Get lecturer's courses
  getMyCourses: async () => {
    if (ENABLE_MOCK) {
      return mockCourse.getMyCourses();
    }

    const response = await apiClient.get("/courses/my-courses");
    return response;
  },

  // Get student's enrolled courses
  getEnrolledCourses: async () => {
    if (ENABLE_MOCK) {
      return mockCourse.getEnrolledCourses();
    }

    const response = await apiClient.get("/courses/enrolled");
    return response;
  },

  // Create new course (lecturer only)
  createCourse: async (courseData) => {
    if (ENABLE_MOCK) {
      return mockCourse.createCourse(courseData);
    }

    const response = await apiClient.post("/courses", courseData);
    return response;
  },

  // Update course (lecturer only)
  updateCourse: async (courseId, courseData) => {
    if (ENABLE_MOCK) {
      return mockCourse.updateCourse(courseId, courseData);
    }

    const response = await apiClient.put(`/courses/${courseId}`, courseData);
    return response;
  },

  // Delete course (lecturer only)
  deleteCourse: async (courseId) => {
    if (ENABLE_MOCK) {
      return mockCourse.deleteCourse(courseId);
    }

    const response = await apiClient.delete(`/courses/${courseId}`);
    return response;
  },

  // Enroll student in course (lecturer only)
  enrollStudent: async (courseId, studentEmail) => {
    if (ENABLE_MOCK) {
      return mockCourse.enrollStudent(courseId, studentEmail);
    }

    const response = await apiClient.post(`/courses/${courseId}/enroll`, {
      student_email: studentEmail,
    });
    return response;
  },

  // Get course students (lecturer only)
  getCourseStudents: async (courseId) => {
    if (ENABLE_MOCK) {
      return mockCourse.getCourseStudents(courseId);
    }

    const response = await apiClient.get(`/courses/${courseId}/students`);
    return response;
  },

  // Get course details
  getCourseDetails: async (courseId) => {
    if (ENABLE_MOCK) {
      return mockCourse.getCourseDetails(courseId);
    }

    const response = await apiClient.get(`/courses/${courseId}`);
    return response;
  },

  // Search available courses
  searchCourses: async (query) => {
    if (ENABLE_MOCK) {
      return mockCourse.searchCourses(query);
    }

    const response = await apiClient.get(
      `/courses/search?q=${encodeURIComponent(query)}`
    );
    return response;
  },
};

// Attendance API
export const attendanceAPI = {
  // Mark attendance (student)
  markAttendance: async (sessionId, faceData = null) => {
    if (ENABLE_MOCK) {
      return mockAttendance.markAttendance(sessionId, faceData);
    }

    const response = await apiClient.post("/attendance/mark", {
      session_id: sessionId,
      face_data: faceData,
    });
    return response;
  },

  // Get my attendance records (student)
  getMyAttendance: async (
    courseId = null,
    startDate = null,
    endDate = null
  ) => {
    if (ENABLE_MOCK) {
      return mockAttendance.getMyAttendance(courseId, startDate, endDate);
    }

    const params = new URLSearchParams();
    if (courseId) params.append("course_id", courseId);
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);

    const response = await apiClient.get(`/attendance/my-attendance?${params}`);
    return response;
  },

  // Get course attendance (lecturer)
  getCourseAttendance: async (courseId, sessionId = null) => {
    if (ENABLE_MOCK) {
      return mockAttendance.getCourseAttendance(courseId, sessionId);
    }

    const params = new URLSearchParams();
    if (sessionId) params.append("session_id", sessionId);

    const response = await apiClient.get(
      `/courses/${courseId}/attendance?${params}`
    );
    return response;
  },

  // Get attendance analytics (lecturer)
  getAttendanceAnalytics: async (courseId = null, period = "month") => {
    if (ENABLE_MOCK) {
      return mockAttendance.getAttendanceAnalytics(courseId, period);
    }

    const params = new URLSearchParams();
    if (courseId) params.append("course_id", courseId);
    params.append("period", period);

    const response = await apiClient.get(`/attendance/analytics?${params}`);
    return response;
  },

  // Create attendance session (lecturer)
  createSession: async (courseId, sessionData) => {
    if (ENABLE_MOCK) {
      return mockAttendance.createSession(courseId, sessionData);
    }

    const response = await apiClient.post(
      `/courses/${courseId}/sessions`,
      sessionData
    );
    return response;
  },

  // Get active sessions (student)
  getActiveSessions: async () => {
    if (ENABLE_MOCK) {
      return mockAttendance.getActiveSessions();
    }

    const response = await apiClient.get("/attendance/active-sessions");
    return response;
  },

  // Get today's attendance summary
  getTodayAttendance: async () => {
    if (ENABLE_MOCK) {
      return mockAttendance.getTodayAttendance();
    }

    const response = await apiClient.get("/attendance/today");
    return response;
  },
};

// Analytics API (lecturer only)
export const analyticsAPI = {
  // Get dashboard statistics
  getDashboardStats: async () => {
    if (ENABLE_MOCK) {
      return mockAnalytics.getDashboardStats();
    }

    const response = await apiClient.get("/analytics/dashboard");
    return response;
  },

  // Get attendance trends
  getAttendanceTrends: async (period = "month", courseId = null) => {
    if (ENABLE_MOCK) {
      return mockAnalytics.getAttendanceTrends(period, courseId);
    }

    const params = new URLSearchParams();
    params.append("period", period);
    if (courseId) params.append("course_id", courseId);

    const response = await apiClient.get(`/analytics/trends?${params}`);
    return response;
  },

  // Get student performance analytics
  getStudentPerformance: async (courseId = null) => {
    if (ENABLE_MOCK) {
      return mockAnalytics.getStudentPerformance(courseId);
    }

    const params = new URLSearchParams();
    if (courseId) params.append("course_id", courseId);

    const response = await apiClient.get(
      `/analytics/student-performance?${params}`
    );
    return response;
  },

  // Export attendance data
  exportAttendanceData: async (
    courseId,
    format = "csv",
    startDate = null,
    endDate = null
  ) => {
    if (ENABLE_MOCK) {
      return mockAnalytics.exportAttendanceData(
        courseId,
        format,
        startDate,
        endDate
      );
    }

    const params = new URLSearchParams();
    params.append("format", format);
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);

    const response = await apiClient.get(
      `/courses/${courseId}/export?${params}`,
      {
        responseType: "blob",
      }
    );
    return response;
  },
};

// Mock data for development
const mockAuth = {
  login: async (credentials) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));

    if (
      credentials.email === "student@student.bowen.edu.ng" &&
      credentials.password === "password"
    ) {
      return {
        data: {
          access_token: "mock_student_token",
          token_type: "bearer",
          user: {
            id: 1,
            full_name: "John Student",
            email: "student@student.bowen.edu.ng",
            role: "student",
            matric_number: "BU/CSC/21/0001",
            college: "College of Information Technology",
            department: "Computer Science",
            level: "400",
            is_face_registered: false,
          },
          expires_in: 86400,
        },
      };
    } else if (
      credentials.email === "lecturer@bowen.edu.ng" &&
      credentials.password === "password"
    ) {
      return {
        data: {
          access_token: "mock_lecturer_token",
          token_type: "bearer",
          user: {
            id: 2,
            full_name: "Dr. Jane Lecturer",
            email: "lecturer@bowen.edu.ng",
            role: "lecturer",
            staff_id: "BU/CSC/2024",
            college: "College of Information Technology",
            department: "Computer Science",
            is_face_registered: true,
            permissions: {
              can_manage_courses: true,
              can_enroll_students: true,
              can_view_analytics: true,
              can_manage_attendance: true,
              has_admin_privileges: true,
            },
          },
          expires_in: 86400,
        },
      };
    } else {
      throw new Error("Invalid credentials");
    }
  },

  registerStudent: async (studentData) => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return {
      data: {
        user: { ...studentData, id: Math.random() },
        message: "Student account created successfully!",
        redirect_to: "/login",
      },
    };
  },

  registerLecturer: async (lecturerData) => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return {
      data: {
        user: { ...lecturerData, id: Math.random() },
        message: "Lecturer account created successfully!",
        redirect_to: "/login",
      },
    };
  },

  getCurrentUser: async () => {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("No token found");

    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      data: {
        success: true,
        user: JSON.parse(localStorage.getItem("user") || "{}"),
      },
    };
  },

  logout: async () => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return { data: { message: "Logged out successfully" } };
  },

  getSystemInfo: async () => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      data: {
        universities: ["Bowen University"],
        colleges: [
          {
            name: "College of Information Technology",
            code: "CIT",
            departments: [
              "Computer Science",
              "Information Technology",
              "Cyber Security",
            ],
          },
          {
            name: "College of Health Sciences",
            code: "CHS",
            departments: ["Anatomy", "Physiology", "Medicine", "Nursing"],
          },
          {
            name: "College of Engineering",
            code: "COE",
            departments: [
              "Electrical Engineering",
              "Mechanical Engineering",
              "Civil Engineering",
            ],
          },
        ],
        levels: ["100", "200", "300", "400", "500"],
        genders: ["Male", "Female", "Other"],
      },
    };
  },

  registerFace: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    return {
      data: {
        message: "Face registered successfully",
        is_face_registered: true,
      },
    };
  },

  verifyFace: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    return {
      data: {
        verified: true,
        user_id: 1,
        confidence: 0.95,
        message: "Face verified successfully",
      },
    };
  },

  changePassword: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        message: "Password changed successfully",
      },
    };
  },

  uploadProfileImage: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return {
      data: {
        message: "Profile image uploaded successfully",
        image_url: "/uploads/profile_images/mock.jpg",
      },
    };
  },
};

// Add other mock services for course, attendance, and analytics
const mockCourse = {
  getMyCourses: async () => {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return {
      data: {
        courses: [
          {
            id: 1,
            course_code: "CSC 438",
            course_title: "Web Programming",
            course_units: 3,
            semester: "First Semester",
            academic_session: "2024/2025",
            level: "400",
            students_count: 25,
            sessions_count: 12,
            created_at: "2024-01-15T00:00:00Z",
          },
        ],
        total: 1,
      },
    };
  },

  getEnrolledCourses: async () => {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return {
      data: {
        courses: [
          {
            id: 1,
            course_code: "CSC 438",
            course_title: "Web Programming",
            lecturer_name: "Dr. Jane Lecturer",
            attendance_percentage: 85,
            total_sessions: 12,
            attended_sessions: 10,
          },
        ],
        total: 1,
      },
    };
  },

  createCourse: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        course: { id: Math.random() },
        message: "Course created successfully",
      },
    };
  },

  updateCourse: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        message: "Course updated successfully",
      },
    };
  },

  deleteCourse: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        message: "Course deleted successfully",
      },
    };
  },

  enrollStudent: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        message: "Student enrolled successfully",
      },
    };
  },

  getCourseStudents: async () => {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return {
      data: {
        students: [
          {
            id: 1,
            full_name: "John Student",
            matric_number: "BU/CSC/21/0001",
            email: "student@student.bowen.edu.ng",
            attendance_percentage: 85,
            is_face_registered: false,
          },
        ],
        total: 1,
      },
    };
  },

  getCourseDetails: async () => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      data: {
        course: {
          id: 1,
          course_code: "CSC 438",
          course_title: "Web Programming",
          course_units: 3,
          description: "Introduction to web programming concepts",
          lecturer_name: "Dr. Jane Lecturer",
        },
      },
    };
  },

  searchCourses: async () => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      data: {
        courses: [],
        total: 0,
      },
    };
  },
};

const mockAttendance = {
  markAttendance: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    return {
      data: {
        message: "Attendance marked successfully",
        attendance_record: {
          id: Math.random(),
          status: "present",
          marked_at: new Date().toISOString(),
        },
      },
    };
  },

  getMyAttendance: async () => {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return {
      data: {
        attendance_records: [
          {
            id: 1,
            course_code: "CSC 438",
            course_title: "Web Programming",
            session_date: "2024-01-15",
            status: "present",
            marked_at: "2024-01-15T09:00:00Z",
          },
        ],
        summary: {
          total_sessions: 12,
          attended_sessions: 10,
          attendance_percentage: 83.33,
        },
      },
    };
  },

  getCourseAttendance: async () => {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return {
      data: {
        attendance_records: [],
        summary: {
          total_students: 25,
          present_students: 20,
          attendance_percentage: 80,
        },
      },
    };
  },

  getAttendanceAnalytics: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        overview: {
          total_sessions: 12,
          average_attendance: 82.5,
          trend: "increasing",
        },
        daily_trends: [],
        course_comparison: [],
      },
    };
  },

  createSession: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        session: { id: Math.random() },
        message: "Attendance session created successfully",
      },
    };
  },

  getActiveSessions: async () => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      data: {
        sessions: [],
        total: 0,
      },
    };
  },

  getTodayAttendance: async () => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      data: {
        today_sessions: 0,
        attended_sessions: 0,
        attendance_percentage: 0,
      },
    };
  },
};

const mockAnalytics = {
  getDashboardStats: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        total_courses: 1,
        total_students: 25,
        active_sessions: 0,
        average_attendance: 82.5,
      },
    };
  },

  getAttendanceTrends: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        trends: [],
        period: "month",
      },
    };
  },

  getStudentPerformance: async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      data: {
        performance_data: [],
        statistics: {
          above_average: 15,
          average: 8,
          below_average: 2,
        },
      },
    };
  },

  exportAttendanceData: async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    return {
      data: new Blob(["mock,csv,data"], { type: "text/csv" }),
    };
  },
};

// Test connection function
export const testConnection = async () => {
  try {
    if (ENABLE_MOCK) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      return { success: true, message: "Mock API connected" };
    }

    const response = await apiClient.get("/health");
    return { success: true, data: response.data };
  } catch (error) {
    console.error("Connection test failed:", error);
    return { success: false, error: error.message };
  }
};

export default apiClient;
