import apiClient from "./apiClient";

export const attendanceService = {
  markAttendance: async (sessionId, imageBlob) => {
    const formData = new FormData();
    formData.append("image", imageBlob, "attendance-photo.jpg");

    const response = await apiClient.post(
      `/attendance/mark/${sessionId}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  getStudentAttendance: async (courseId = null) => {
    const params = courseId ? { course_id: courseId } : {};
    const response = await apiClient.get("/attendance/student/my-attendance", {
      params,
    });
    return response.data;
  },

  getCourseAnalytics: async (courseId) => {
    const response = await apiClient.get(
      `/attendance/course/${courseId}/analytics`
    );
    return response.data;
  },

  activateSession: async (sessionId) => {
    const response = await apiClient.post(
      `/attendance/session/${sessionId}/activate`
    );
    return response.data;
  },

  deactivateSession: async (sessionId) => {
    const response = await apiClient.post(
      `/attendance/session/${sessionId}/deactivate`
    );
    return response.data;
  },

  getTodayAttendance: async () => {
    const response = await apiClient.get("/attendance/today");
    return response.data;
  },

  getWeeklyStats: async () => {
    const response = await apiClient.get("/attendance/weekly-stats");
    return response.data;
  },

  getMonthlyStats: async () => {
    const response = await apiClient.get("/attendance/monthly-stats");
    return response.data;
  },
};
