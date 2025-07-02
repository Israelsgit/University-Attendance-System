import React, { createContext, useContext, useState, useEffect } from "react";
import { authService } from "../services/auth";
import toast from "react-hot-toast";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  // Check if user is already logged in on app start
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("attendance_token");
        if (token) {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        localStorage.removeItem("attendance_token");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    try {
      setIsAuthenticating(true);
      const response = await authService.login(credentials);

      if (response.access_token && response.user) {
        localStorage.setItem("attendance_token", response.access_token);
        setUser(response.user);
        toast.success(`Welcome back, ${response.user.name}!`);
        return { success: true };
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || error.message || "Login failed";
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsAuthenticating(false);
    }
  };

  const register = async (userData) => {
    try {
      setIsAuthenticating(true);
      const response = await authService.register(userData);

      if (response.token && response.user) {
        localStorage.setItem("attendance_token", response.token);
        setUser(response.user);
        toast.success(
          `Welcome ${response.user.name}! Your account has been created.`
        );
        return { success: true };
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || error.message || "Registration failed";
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsAuthenticating(false);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem("attendance_token");
      setUser(null);
      toast.success("You have been logged out successfully");
    }
  };

  const updateProfile = async (updates) => {
    try {
      const updatedUser = await authService.updateProfile(updates);
      setUser(updatedUser);
      toast.success("Profile updated successfully");
      return { success: true };
    } catch (error) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Profile update failed";
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const uploadProfileImage = async (imageFile) => {
    try {
      const updatedUser = await authService.uploadProfileImage(imageFile);
      setUser(updatedUser);
      toast.success("Profile image updated successfully");
      return { success: true };
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || error.message || "Image upload failed";
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const changePassword = async (passwordData) => {
    try {
      await authService.changePassword(passwordData);
      toast.success("Password changed successfully");
      return { success: true };
    } catch (error) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Password change failed";
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const value = {
    user,
    loading,
    isAuthenticating,
    login,
    register,
    logout,
    updateProfile,
    uploadProfileImage,
    changePassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export { AuthContext };
