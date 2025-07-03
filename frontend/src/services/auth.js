// frontend/src/services/auth.js
import api from "./apiClient";

export const authService = {
  // Login user
  login: async (credentials) => {
    try {
      console.log("🔐 AuthService: Attempting login...", {
        email: credentials.email,
        user_type: credentials.user_type,
      });

      // Create FormData for the login request
      const formData = new FormData();
      formData.append("email", credentials.email);
      formData.append("password", credentials.password);
      formData.append("user_type", credentials.user_type || "student");

      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      console.log("✅ AuthService: Login successful", response.data);
      return response;
    } catch (error) {
      console.error("❌ AuthService: Login failed", error);
      throw error;
    }
  },

  // Register new student
  register: async (userData) => {
    try {
      console.log(
        "📝 AuthService: Attempting registration...",
        userData.full_name
      );

      const formData = new FormData();

      // Add all text fields to FormData
      const textFields = [
        "full_name",
        "email",
        "password",
        "phone",
        "gender",
        "date_of_birth",
        "address",
        "college",
        "department",
        "programme",
        "level",
        "matric_number",
        "university",
        "role",
      ];

      textFields.forEach((field) => {
        if (userData[field] && userData[field] !== "") {
          formData.append(field, userData[field]);
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

      console.log("✅ AuthService: Registration successful", response.data);
      return response;
    } catch (error) {
      console.error("❌ AuthService: Registration failed", error);
      throw error;
    }
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      console.log("👤 AuthService: Fetching current user...");
      const response = await api.get("/auth/me");
      console.log("✅ AuthService: User data retrieved", response.data.user);
      return response;
    } catch (error) {
      console.error("❌ AuthService: Failed to get current user", error);
      throw error;
    }
  },

  // Logout user
  logout: async () => {
    try {
      console.log("👋 AuthService: Logging out...");
      await api.post("/auth/logout");
      console.log("✅ AuthService: Logout successful");
    } catch (error) {
      console.error("❌ AuthService: Logout error", error);
      // Even if logout fails on server, we still want to clear local storage
    }
  },

  // Update user profile
  updateProfile: async (updates) => {
    try {
      console.log("🔄 AuthService: Updating profile...");

      const formData = new FormData();

      // Add text fields
      const textFields = ["full_name", "phone", "address"];
      textFields.forEach((field) => {
        if (updates[field] !== undefined) {
          formData.append(field, updates[field]);
        }
      });

      // Add profile image if provided
      if (updates.profileImage) {
        formData.append("profileImage", updates.profileImage);
      }

      const response = await api.put("/auth/profile", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      console.log("✅ AuthService: Profile updated", response.data);
      return response;
    } catch (error) {
      console.error("❌ AuthService: Profile update failed", error);
      throw error;
    }
  },

  // Upload/register face for attendance
  registerFace: async (imageFile) => {
    try {
      console.log("📷 AuthService: Registering face...");

      const formData = new FormData();
      formData.append("image", imageFile);

      const response = await api.post("/auth/face-registration", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      console.log("✅ AuthService: Face registered", response.data);
      return response;
    } catch (error) {
      console.error("❌ AuthService: Face registration failed", error);
      throw error;
    }
  },

  // Change password
  changePassword: async (passwordData) => {
    try {
      console.log("🔒 AuthService: Changing password...");

      const formData = new FormData();
      formData.append("current_password", passwordData.currentPassword);
      formData.append("new_password", passwordData.newPassword);

      const response = await api.put("/auth/password", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      console.log("✅ AuthService: Password changed", response.data);
      return response;
    } catch (error) {
      console.error("❌ AuthService: Password change failed", error);
      throw error;
    }
  },

  // Register lecturer (admin only)
  registerLecturer: async (lecturerData) => {
    try {
      console.log(
        "👨‍🏫 AuthService: Registering lecturer...",
        lecturerData.full_name
      );

      const formData = new FormData();

      // Add all lecturer fields
      const lecturerFields = [
        "full_name",
        "email",
        "staff_id",
        "password",
        "college",
        "department",
        "programme",
        "phone",
        "gender",
        "university",
      ];

      lecturerFields.forEach((field) => {
        if (lecturerData[field] && lecturerData[field] !== "") {
          formData.append(field, lecturerData[field]);
        }
      });

      const response = await api.post("/auth/register/lecturer", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      console.log("✅ AuthService: Lecturer registered", response.data);
      return response;
    } catch (error) {
      console.error("❌ AuthService: Lecturer registration failed", error);
      throw error;
    }
  },

  // Check auth service health
  checkHealth: async () => {
    try {
      const response = await api.get("/auth/health");
      return response.data;
    } catch (error) {
      console.error("❌ AuthService: Health check failed", error);
      throw error;
    }
  },

  // Validate token without making API call
  isTokenValid: () => {
    const token = localStorage.getItem("token");
    if (!token) return false;

    try {
      // Basic token validation (you might want to add JWT decode and expiry check)
      const tokenParts = token.split(".");
      if (tokenParts.length !== 3) return false;

      // Decode payload to check expiry
      const payload = JSON.parse(atob(tokenParts[1]));
      const currentTime = Date.now() / 1000;

      return payload.exp > currentTime;
    } catch (error) {
      console.error("Token validation error:", error);
      return false;
    }
  },

  // Clear all auth data
  clearAuthData: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    console.log("🧹 AuthService: Auth data cleared");
  },
};
