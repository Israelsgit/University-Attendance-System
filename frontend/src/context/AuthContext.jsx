// frontend/src/context/AuthContext.jsx
import React, { createContext, useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import { authService } from "../services/auth";
import { testConnection } from "../services/apiClient";

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);

  // Test API connection on mount
  useEffect(() => {
    const checkApiConnection = async () => {
      try {
        const result = await testConnection();
        setApiConnected(result.success);
        if (!result.success) {
          toast.error(
            "Cannot connect to server. Please check if the backend is running."
          );
        }
      } catch (error) {
        console.error("API connection test failed:", error);
        setApiConnected(false);
      }
    };

    checkApiConnection();
  }, []);

  // Check for existing authentication on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem("token");
        const userData = localStorage.getItem("user");

        if (token && userData) {
          // Verify token is still valid by fetching current user
          try {
            const response = await authService.getCurrentUser();
            if (response.data.success) {
              setUser(response.data.user);
              setIsAuthenticated(true);
              console.log("✅ User session restored:", response.data.user);
            } else {
              // Token invalid, clear storage
              clearAuthData();
            }
          } catch (error) {
            console.error("Token validation failed:", error);
            clearAuthData();
          }
        }
      } catch (error) {
        console.error("Auth initialization error:", error);
        clearAuthData();
      } finally {
        setLoading(false);
      }
    };

    if (apiConnected) {
      initializeAuth();
    } else {
      setLoading(false);
    }
  }, [apiConnected]);

  const clearAuthData = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const login = useCallback(
    async (credentials) => {
      if (!apiConnected) {
        toast.error("Cannot connect to server. Please try again later.");
        return { success: false, error: "Server connection failed" };
      }

      setIsAuthenticating(true);

      try {
        console.log("🔐 Attempting login with:", {
          email: credentials.email,
          user_type: credentials.user_type,
        });

        const response = await authService.login(credentials);

        console.log("🔐 Login response:", response.data);

        if (response.data && response.data.access_token) {
          const { access_token, user: userData } = response.data;

          // Store authentication data
          localStorage.setItem("token", access_token);
          localStorage.setItem("user", JSON.stringify(userData));

          // Update state
          setUser(userData);
          setIsAuthenticated(true);

          toast.success(`Welcome back, ${userData.full_name}!`);
          console.log("✅ Login successful:", userData);

          return {
            success: true,
            user: userData,
            token: access_token,
          };
        } else {
          const errorMsg = response.data?.message || "Login failed";
          toast.error(errorMsg);
          return {
            success: false,
            error: errorMsg,
          };
        }
      } catch (error) {
        console.error("❌ Login error:", error);

        let errorMessage = "Login failed. Please try again.";

        if (error.status === 401) {
          errorMessage = "Invalid email or password.";
        } else if (error.status === 403) {
          errorMessage = "Account is deactivated. Contact administrator.";
        } else if (error.message) {
          errorMessage = error.message;
        }

        toast.error(errorMessage);
        return {
          success: false,
          error: errorMessage,
        };
      } finally {
        setIsAuthenticating(false);
      }
    },
    [apiConnected]
  );

  const register = useCallback(
    async (userData) => {
      if (!apiConnected) {
        toast.error("Cannot connect to server. Please try again later.");
        return { success: false, error: "Server connection failed" };
      }

      setIsAuthenticating(true);

      try {
        console.log("📝 Attempting registration for:", userData.full_name);

        const response = await authService.register(userData);

        console.log("📝 Registration response:", response.data);

        if (response.data && response.data.user) {
          toast.success(
            "Registration successful! Please login with your credentials."
          );
          console.log("✅ Registration successful:", response.data.user);

          return {
            success: true,
            user: response.data.user,
            message: response.data.message,
          };
        } else {
          const errorMsg = response.data?.message || "Registration failed";
          toast.error(errorMsg);
          return {
            success: false,
            error: errorMsg,
          };
        }
      } catch (error) {
        console.error("❌ Registration error:", error);

        let errorMessage = "Registration failed. Please try again.";

        if (error.status === 400) {
          errorMessage = error.message || "Invalid registration data.";
        } else if (error.errors) {
          // Handle validation errors
          errorMessage = "Please check your information and try again.";
        } else if (error.message) {
          errorMessage = error.message;
        }

        toast.error(errorMessage);
        return {
          success: false,
          error: errorMessage,
          errors: error.errors,
        };
      } finally {
        setIsAuthenticating(false);
      }
    },
    [apiConnected]
  );

  const logout = useCallback(async () => {
    setIsAuthenticating(true);

    try {
      // Call backend logout endpoint
      await authService.logout();
    } catch (error) {
      console.error("Logout error:", error);
      // Continue with local logout even if backend call fails
    } finally {
      // Clear local auth data
      clearAuthData();
      setIsAuthenticating(false);
      toast.success("Logged out successfully");
      console.log("✅ User logged out");
    }
  }, [clearAuthData]);

  const updateProfile = useCallback(
    async (updates) => {
      if (!user) return { success: false, error: "Not authenticated" };

      try {
        const response = await authService.updateProfile(updates);

        if (response.data && response.data.user) {
          const updatedUser = response.data.user;
          setUser(updatedUser);
          localStorage.setItem("user", JSON.stringify(updatedUser));
          toast.success("Profile updated successfully");
          return { success: true, user: updatedUser };
        }

        return { success: false, error: "Update failed" };
      } catch (error) {
        console.error("Profile update error:", error);
        toast.error(error.message || "Failed to update profile");
        return { success: false, error: error.message };
      }
    },
    [user]
  );

  const refreshUser = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      const response = await authService.getCurrentUser();
      if (response.data && response.data.user) {
        setUser(response.data.user);
        localStorage.setItem("user", JSON.stringify(response.data.user));
      }
    } catch (error) {
      console.error("Failed to refresh user:", error);
      // If refresh fails, logout user
      logout();
    }
  }, [isAuthenticated, logout]);

  const contextValue = {
    // State
    user,
    isAuthenticated,
    isAuthenticating,
    loading,
    apiConnected,

    // Actions
    login,
    register,
    logout,
    updateProfile,
    refreshUser,
    clearAuthData,

    // User role helpers
    isStudent: user?.role === "student",
    isLecturer: user?.role === "lecturer",
    isAdmin: user?.role === "admin",
    canManageClasses: user?.role === "lecturer" || user?.role === "admin",
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};
