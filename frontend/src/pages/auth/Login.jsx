import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { toast } from "react-hot-toast";
import { LogIn, User, GraduationCap, Eye, EyeOff } from "lucide-react";

import Button from "../../components/common/Button";
import Input from "../../components/common/Input";
import LoadingSpinner from "../../components/common/LoadingSpinner";
import { useAuth } from "../../hooks/useAuth";

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loading: authLoading } = useAuth();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    userType: "student", // Default to student, removed admin
  });

  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});

  // Check for registration success message
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const registered = searchParams.get("registered");
    const userType = searchParams.get("userType");

    if (registered === "true") {
      toast.success(`${userType} account created successfully! Please login.`);
    }
  }, [location]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const handleUserTypeChange = (userType) => {
    setFormData((prev) => ({
      ...prev,
      userType,
    }));
    setErrors({});
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error("Please fill in all required fields correctly");
      return;
    }

    setIsAuthenticating(true);

    try {
      await login({
        email: formData.email,
        password: formData.password,
        user_type: formData.userType,
      });

      toast.success("Login successful!");

      // Redirect based on user type
      const redirectTo = location.state?.from?.pathname || "/dashboard";
      navigate(redirectTo, { replace: true });
    } catch (error) {
      console.error("Login error:", error);

      let errorMessage = "Login failed. Please try again.";

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }

      toast.error(errorMessage);
    } finally {
      setIsAuthenticating(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-4">
            <GraduationCap className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-gray-400">Bowen University Attendance System</p>
          <p className="text-sm text-gray-500">
            Sign in to access your account
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/10 p-6 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Account Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Account Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => handleUserTypeChange("student")}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    formData.userType === "student"
                      ? "bg-blue-600 border-blue-500 text-white"
                      : "bg-white/5 border-gray-600 text-gray-300 hover:bg-white/10"
                  }`}
                >
                  <User className="h-4 w-4 mx-auto mb-1" />
                  <span className="text-sm font-medium">Student</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleUserTypeChange("lecturer")}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    formData.userType === "lecturer"
                      ? "bg-blue-600 border-blue-500 text-white"
                      : "bg-white/5 border-gray-600 text-gray-300 hover:bg-white/10"
                  }`}
                >
                  <GraduationCap className="h-4 w-4 mx-auto mb-1" />
                  <span className="text-sm font-medium">Lecturer</span>
                </button>
              </div>
            </div>

            {/* Email Input */}
            <div>
              <Input
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder={
                  formData.userType === "student"
                    ? "Email address (e.g., yourname@student.bowen.edu.ng)"
                    : "Email address (e.g., yourname@bowen.edu.ng)"
                }
                error={errors.email}
                required
              />
            </div>

            {/* Password Input */}
            <div>
              <div className="relative">
                <Input
                  label="Password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Enter your password"
                  error={errors.password}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-[38px] text-gray-400 hover:text-gray-300"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 bg-white/10 border-gray-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-300">Remember me</span>
              </label>
              <Link
                to="/forgot-password"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Forgot password?
              </Link>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              size="large"
              fullWidth
              loading={isAuthenticating}
              className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              <LogIn className="h-5 w-5 mr-2 group-hover:scale-110 transition-transform" />
              Sign In
            </Button>
          </form>

          {/* User Type Info */}
          <div className="mt-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
            <div className="text-xs text-blue-200">
              {formData.userType === "student" && (
                <div>
                  <strong>Students:</strong> Access your attendance records and
                  mark attendance.
                  <br />
                  Use your university email or matriculation number.
                </div>
              )}
              {formData.userType === "lecturer" && (
                <div>
                  <strong>Lecturers:</strong> Manage courses, student
                  enrollment, and attendance.
                  <br />
                  You have full administrative access to the system.
                </div>
              )}
            </div>
          </div>

          {/* Registration Links */}
          <div className="mt-6 space-y-3">
            {formData.userType === "student" && (
              <p className="text-center text-sm text-gray-400">
                New student at Bowen University?{" "}
                <Link
                  to="/register/student"
                  className="font-medium text-blue-400 hover:text-blue-300 transition-colors"
                >
                  Register here
                </Link>
              </p>
            )}

            {formData.userType === "lecturer" && (
              <p className="text-center text-sm text-gray-400">
                New lecturer at Bowen University?{" "}
                <Link
                  to="/register/lecturer"
                  className="font-medium text-blue-400 hover:text-blue-300 transition-colors"
                >
                  Register here
                </Link>
              </p>
            )}
          </div>

          {/* Alternative Registration */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">
              {formData.userType === "student"
                ? "Are you a lecturer?"
                : "Are you a student?"}{" "}
              <button
                type="button"
                onClick={() =>
                  handleUserTypeChange(
                    formData.userType === "student" ? "lecturer" : "student"
                  )
                }
                className="text-blue-400 hover:text-blue-300 transition-colors"
              >
                Switch here
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
