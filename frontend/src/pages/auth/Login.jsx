import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Eye,
  EyeOff,
  LogIn,
  GraduationCap,
  UserCheck,
  Users,
} from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import Button from "../../components/common/Button";
import Input from "../../components/common/Input";

const Login = () => {
  const { login, isAuthenticating } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "", // Now always email for backend
    password: "",
    userType: "student", // Used for user_type in backend
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
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

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    const loginData = {
      email: formData.email.trim(),
      password: formData.password,
      user_type: formData.userType,
    };

    const result = await login(loginData);
    if (result.success) {
      setTimeout(() => {
        navigate("/dashboard");
      }, 100);
    }
  };

  const getPlaceholderText = () => {
    return "Email address (e.g., yourname@student.bowen.edu.ng)";
  };

  const getIdentifierLabel = () => {
    return "Email Address";
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-20 w-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-2xl">
            <GraduationCap className="h-10 w-10 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Welcome Back</h2>
          <p className="text-gray-300">Bowen University Attendance System</p>
          <p className="text-sm text-gray-400 mt-2">
            Sign in to access your account
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-glass border border-white/20 p-8">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* User Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Account Type
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() =>
                    setFormData((prev) => ({ ...prev, userType: "student" }))
                  }
                  className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                    formData.userType === "student"
                      ? "border-green-500 bg-green-500/20 text-white"
                      : "border-white/20 bg-white/5 text-gray-300 hover:border-white/30"
                  }`}
                >
                  <Users className="h-4 w-4 mx-auto mb-1" />
                  <span className="text-xs font-medium">Student</span>
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setFormData((prev) => ({ ...prev, userType: "lecturer" }))
                  }
                  className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                    formData.userType === "lecturer"
                      ? "border-blue-500 bg-blue-500/20 text-white"
                      : "border-white/20 bg-white/5 text-gray-300 hover:border-white/30"
                  }`}
                >
                  <UserCheck className="h-4 w-4 mx-auto mb-1" />
                  <span className="text-xs font-medium">Lecturer</span>
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setFormData((prev) => ({ ...prev, userType: "admin" }))
                  }
                  className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                    formData.userType === "admin"
                      ? "border-purple-500 bg-purple-500/20 text-white"
                      : "border-white/20 bg-white/5 text-gray-300 hover:border-white/30"
                  }`}
                >
                  <GraduationCap className="h-4 w-4 mx-auto mb-1" />
                  <span className="text-xs font-medium">Admin</span>
                </button>
              </div>
            </div>

            <div>
              <Input
                label={getIdentifierLabel()}
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                error={errors.email}
                placeholder={getPlaceholderText()}
                required
              />
            </div>

            <div>
              <div className="relative">
                <Input
                  label="Password"
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  error={errors.password}
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  className="absolute right-3 top-9 text-gray-400 hover:text-white transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded bg-white/10 border-white/20"
                />
                <label
                  htmlFor="remember-me"
                  className="ml-2 block text-sm text-gray-300"
                >
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <a
                  href="#"
                  className="font-medium text-blue-400 hover:text-blue-300 transition-colors"
                >
                  Forgot password?
                </a>
              </div>
            </div>

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
                  class schedules.
                  <br />
                  Use your matric number (e.g., BU/CSC/21/0001) or university
                  email.
                </div>
              )}
              {formData.userType === "lecturer" && (
                <div>
                  <strong>Lecturers:</strong> Manage class attendance and
                  student records.
                  <br />
                  Use your staff ID (e.g., BU/CSC/2024) or university email.
                </div>
              )}
              {formData.userType === "admin" && (
                <div>
                  <strong>Administrators:</strong> System-wide management and
                  analytics.
                  <br />
                  Use your admin credentials to access all system features.
                </div>
              )}
            </div>
          </div>

          {/* Register link - Only show for students */}
          {formData.userType === "student" && (
            <p className="mt-6 text-center text-sm text-gray-400">
              New student at Bowen University?{" "}
              <Link
                to="/register"
                className="font-medium text-blue-400 hover:text-blue-300 transition-colors"
              >
                Register here
              </Link>
            </p>
          )}

          {/* Note for staff */}
          {(formData.userType === "lecturer" ||
            formData.userType === "admin") && (
            <p className="mt-6 text-center text-xs text-gray-500">
              Staff accounts are created by the IT department.
              <br />
              Contact admin if you need assistance.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Login;
