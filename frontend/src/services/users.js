import api from "./api";

export const usersService = {
  // Get all users (admin only)
  getAllUsers: async (filters = {}) => {
    try {
      const params = new URLSearchParams(filters);
      const response = await api.get(`/users?${params}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user by ID
  getUserById: async (userId) => {
    try {
      const response = await api.get(`/users/${userId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Update user (admin only)
  updateUser: async (userId, updates) => {
    try {
      const response = await api.put(`/users/${userId}`, updates);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Delete user (admin only)
  deleteUser: async (userId) => {
    try {
      const response = await api.delete(`/users/${userId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user statistics
  getUserStats: async (userId) => {
    try {
      const response = await api.get(`/users/${userId}/stats`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user attendance summary
  getUserAttendanceSummary: async (userId, period = "month") => {
    try {
      const response = await api.get(
        `/users/${userId}/attendance-summary?period=${period}`
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Bulk upload users (admin only)
  bulkUploadUsers: async (csvFile) => {
    try {
      const formData = new FormData();
      formData.append("csvFile", csvFile);

      const response = await api.post("/users/bulk-upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return response;
    } catch (error) {
      throw error;
    }
  },

  // Export users data (admin only)
  exportUsers: async (format = "csv") => {
    try {
      const response = await api.get(`/users/export?format=${format}`, {
        responseType: "blob",
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `users-${new Date().toISOString().split("T")[0]}.${format}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return { success: true };
    } catch (error) {
      throw error;
    }
  },

  // Search users
  searchUsers: async (query) => {
    try {
      const response = await api.get(
        `/users/search?q=${encodeURIComponent(query)}`
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user roles and permissions
  getUserRoles: async (userId) => {
    try {
      const response = await api.get(`/users/${userId}/roles`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Update user roles (admin only)
  updateUserRoles: async (userId, roles) => {
    try {
      const response = await api.put(`/users/${userId}/roles`, { roles });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get user activity log
  getUserActivityLog: async (userId, limit = 50) => {
    try {
      const response = await api.get(
        `/users/${userId}/activity?limit=${limit}`
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Reset user password (admin only)
  resetUserPassword: async (userId) => {
    try {
      const response = await api.post(`/users/${userId}/reset-password`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Toggle user active status (admin only)
  toggleUserStatus: async (userId, isActive) => {
    try {
      const response = await api.put(`/users/${userId}/status`, { isActive });
      return response;
    } catch (error) {
      throw error;
    }
  },
};
