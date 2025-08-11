// Cleaned Users Service - Admin functions removed
import api from "./apiClient";

export const userService = {
  // Get current user profile
  getCurrentUser: async () => {
    try {
      const response = await api.get("/auth/me");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Update user profile
  updateProfile: async (userData) => {
    try {
      const response = await api.put("/users/profile", userData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Change password
  changePassword: async (passwordData) => {
    try {
      const response = await api.post("/auth/change-password", passwordData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Upload profile image
  uploadProfileImage: async (imageFile) => {
    try {
      const formData = new FormData();
      formData.append("file", imageFile);

      const response = await api.post("/auth/upload-profile-image", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user's courses (for students)
  getUserCourses: async () => {
    try {
      const response = await api.get("/courses/enrolled");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user's attendance records
  getUserAttendance: async (
    courseId = null,
    startDate = null,
    endDate = null
  ) => {
    try {
      const params = new URLSearchParams();
      if (courseId) params.append("course_id", courseId);
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);

      const response = await api.get(`/attendance/my-attendance?${params}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Register face for attendance
  registerFace: async (faceData) => {
    try {
      const response = await api.post("/auth/register-face", faceData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get system info for forms
  getSystemInfo: async () => {
    try {
      const response = await api.get("/auth/system-info");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // For lecturers: Get students in their courses
  getCourseStudents: async (courseId) => {
    try {
      const response = await api.get(`/courses/${courseId}/students`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // For lecturers: Search students for enrollment
  searchStudents: async (query) => {
    try {
      const response = await api.get(
        `/users/search/students?q=${encodeURIComponent(query)}`
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user activity log (own activity only)
  getUserActivityLog: async (limit = 50) => {
    try {
      const response = await api.get(`/users/activity?limit=${limit}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user statistics
  getUserStats: async () => {
    try {
      const response = await api.get("/users/stats");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // For lecturers: Get all students (for course enrollment)
  getAllStudents: async (page = 1, limit = 20) => {
    try {
      const response = await api.get(
        `/users/students?page=${page}&limit=${limit}`
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // For lecturers: Get all lecturers (for system overview)
  getAllLecturers: async (page = 1, limit = 20) => {
    try {
      const response = await api.get(
        `/users/lecturers?page=${page}&limit=${limit}`
      );
      return response;
    } catch (error) {
      throw error;
    }
  },
};
