import apiClient from "./apiClient";

export const courseService = {
  getMyCourses: async () => {
    const response = await apiClient.get("/courses/my-courses");
    return response.data;
  },

  createCourse: async (courseData) => {
    const response = await apiClient.post("/courses", courseData);
    return response.data;
  },

  enrollStudent: async (courseId, studentEmail) => {
    const response = await apiClient.post(`/courses/${courseId}/enroll`, {
      student_email: studentEmail,
    });
    return response.data;
  },

  createSession: async (courseId, sessionData) => {
    const response = await apiClient.post(
      `/courses/${courseId}/sessions`,
      sessionData
    );
    return response.data;
  },

  getAvailableSessions: async () => {
    // Mock implementation - replace with actual API call
    return [];
  },
};
