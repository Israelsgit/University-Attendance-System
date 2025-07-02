import api from "./api";

export const authService = {
  // Login user
  login: async (credentials) => {
    try {
      const response = await api.post("/auth/login", credentials);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Register new user
  register: async (userData) => {
    try {
      const formData = new FormData();

      // Add text fields
      Object.keys(userData).forEach((key) => {
        if (key !== "profileImage" && userData[key]) {
          formData.append(key, userData[key]);
        }
      });

      // Add profile image if provided
      if (userData.profileImage) {
        formData.append("profileImage", userData.profileImage);
      }

      const response = await api.post("/auth/register", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return response;
    } catch (error) {
      throw error;
    }
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      const response = await api.get("/auth/me");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Logout user
  logout: async () => {
    try {
      await api.post("/auth/logout");
    } catch (error) {
      // Even if logout fails on server, we still want to clear local storage
      console.error("Logout error:", error);
    }
  },

  // Update user profile
  updateProfile: async (updates) => {
    try {
      const response = await api.put("/auth/profile", updates);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Upload profile image
  uploadProfileImage: async (imageFile) => {
    try {
      const formData = new FormData();
      formData.append("profileImage", imageFile);

      const response = await api.post("/auth/profile/image", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return response;
    } catch (error) {
      throw error;
    }
  },

  // Change password
  changePassword: async (passwordData) => {
    try {
      const response = await api.put("/auth/password", passwordData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Forgot password
  forgotPassword: async (email) => {
    try {
      const response = await api.post("/auth/forgot-password", { email });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Reset password
  resetPassword: async (token, newPassword) => {
    try {
      const response = await api.post("/auth/reset-password", {
        token,
        password: newPassword,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Verify email
  verifyEmail: async (token) => {
    try {
      const response = await api.post("/auth/verify-email", { token });
      return response;
    } catch (error) {
      throw error;
    }
  },
};
