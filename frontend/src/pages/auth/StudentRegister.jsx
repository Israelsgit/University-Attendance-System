import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import { UserPlus, GraduationCap, Eye, EyeOff, ArrowLeft } from "lucide-react";

import Button from "../../components/common/Button";
import Input from "../../components/common/Input";
import Select from "../../components/common/Select";
import LoadingSpinner from "../../components/common/LoadingSpinner";
import { authAPI } from "../../services/apiClient";

const StudentRegister = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    matric_number: "",
    password: "",
    confirm_password: "",
    university: "Bowen University",
    college: "",
    department: "",
    programme: "",
    level: "",
    phone: "",
    gender: "",
  });

  const [systemInfo, setSystemInfo] = useState({
    colleges: [],
    levels: [],
    genders: [],
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [currentStep, setCurrentStep] = useState(1);

  // Load system information
  useEffect(() => {
    const loadSystemInfo = async () => {
      try {
        const response = await authAPI.getSystemInfo();
        setSystemInfo(response.data);
      } catch (error) {
        console.error("Failed to load system info:", error);
        // Fallback data
        setSystemInfo({
          colleges: [
            {
              name: "College of Information Technology",
              departments: [
                "Computer Science",
                "Information Technology",
                "Cyber Security",
              ],
            },
            {
              name: "College of Health Sciences",
              departments: ["Anatomy", "Physiology", "Medicine", "Nursing"],
            },
            {
              name: "College of Engineering",
              departments: [
                "Electrical Engineering",
                "Mechanical Engineering",
                "Civil Engineering",
              ],
            },
          ],
          levels: ["100", "200", "300", "400", "500"],
          genders: ["Male", "Female", "Other"],
        });
      }
    };

    loadSystemInfo();
  }, []);

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

    // Auto-populate programme when department changes
    if (name === "department") {
      setFormData((prev) => ({
        ...prev,
        programme: value,
      }));
    }
  };

  const validateStep = (step) => {
    const newErrors = {};

    if (step === 1) {
      if (!formData.full_name) newErrors.full_name = "Full name is required";
      if (!formData.email) {
        newErrors.email = "Email is required";
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = "Please enter a valid email";
      } else if (
        !formData.email.includes("@student.bowen.edu.ng") &&
        !formData.email.includes("@bowen.edu.ng")
      ) {
        newErrors.email = "Please use your university email address";
      }

      if (!formData.matric_number) {
        newErrors.matric_number = "Matriculation number is required";
      } else if (
        !/^[A-Z]{2,4}\/[A-Z]{2,4}\/\d{2}\/\d{4}$/i.test(formData.matric_number)
      ) {
        newErrors.matric_number = "Invalid format. Use: BU/CSC/21/0001";
      }
    }

    if (step === 2) {
      if (!formData.college) newErrors.college = "College is required";
      if (!formData.department) newErrors.department = "Department is required";
      if (!formData.programme) newErrors.programme = "Programme is required";
      if (!formData.level) newErrors.level = "Level is required";
    }

    if (step === 3) {
      if (!formData.password) {
        newErrors.password = "Password is required";
      } else if (formData.password.length < 6) {
        newErrors.password = "Password must be at least 6 characters";
      }

      if (!formData.confirm_password) {
        newErrors.confirm_password = "Please confirm your password";
      } else if (formData.password !== formData.confirm_password) {
        newErrors.confirm_password = "Passwords do not match";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep((prev) => prev - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateStep(3)) {
      return;
    }

    setIsSubmitting(true);

    try {
      await authAPI.registerStudent(formData);

      toast.success("Student account created successfully!");
      navigate("/login?registered=true&userType=Student");
    } catch (error) {
      console.error("Registration error:", error);

      let errorMessage = "Registration failed. Please try again.";

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }

      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDepartments = () => {
    const selectedCollege = systemInfo.colleges.find(
      (c) => c.name === formData.college
    );
    return selectedCollege ? selectedCollege.departments : [];
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white mb-4">
              Personal Information
            </h3>

            <Input
              label="Full Name"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              placeholder="Enter your full name"
              error={errors.full_name}
              required
            />

            <Input
              label="University Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="yourname@student.bowen.edu.ng"
              error={errors.email}
              required
            />

            <Input
              label="Matriculation Number"
              name="matric_number"
              value={formData.matric_number}
              onChange={handleInputChange}
              placeholder="BU/CSC/21/0001"
              error={errors.matric_number}
              required
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Phone Number (Optional)"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="+234 800 000 0000"
              />

              <Select
                label="Gender (Optional)"
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
                options={systemInfo.genders.map((g) => ({
                  value: g,
                  label: g,
                }))}
                placeholder="Select gender"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white mb-4">
              Academic Information
            </h3>

            <Select
              label="College"
              name="college"
              value={formData.college}
              onChange={handleInputChange}
              options={systemInfo.colleges.map((c) => ({
                value: c.name,
                label: c.name,
              }))}
              placeholder="Select your college"
              error={errors.college}
              required
            />

            <Select
              label="Department"
              name="department"
              value={formData.department}
              onChange={handleInputChange}
              options={getDepartments().map((d) => ({ value: d, label: d }))}
              placeholder="Select your department"
              error={errors.department}
              required
              disabled={!formData.college}
            />

            <Input
              label="Programme"
              name="programme"
              value={formData.programme}
              onChange={handleInputChange}
              placeholder="e.g., Computer Science"
              error={errors.programme}
              required
            />

            <Select
              label="Current Level"
              name="level"
              value={formData.level}
              onChange={handleInputChange}
              options={systemInfo.levels.map((l) => ({
                value: l,
                label: `${l} Level`,
              }))}
              placeholder="Select your level"
              error={errors.level}
              required
            />
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white mb-4">Security</h3>

            <div className="relative">
              <Input
                label="Password"
                name="password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Create a password"
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

            <div className="relative">
              <Input
                label="Confirm Password"
                name="confirm_password"
                type={showConfirmPassword ? "text" : "password"}
                value={formData.confirm_password}
                onChange={handleInputChange}
                placeholder="Confirm your password"
                error={errors.confirm_password}
                required
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-[38px] text-gray-400 hover:text-gray-300"
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>

            <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/20">
              <p className="text-sm text-blue-200">
                <strong>Password Requirements:</strong>
                <br />• At least 6 characters long
                <br />• Use a unique password you haven't used elsewhere
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link
            to="/login"
            className="inline-flex items-center text-blue-400 hover:text-blue-300 transition-colors mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Login
          </Link>

          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-4">
            <GraduationCap className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Student Registration
          </h1>
          <p className="text-gray-400">Bowen University Attendance System</p>
          <p className="text-sm text-gray-500">Create your student account</p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            {[1, 2, 3].map((step) => (
              <div
                key={step}
                className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                  currentStep >= step
                    ? "bg-blue-600 text-white"
                    : "bg-gray-600 text-gray-400"
                }`}
              >
                {step}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-400">
            <span>Personal</span>
            <span>Academic</span>
            <span>Security</span>
          </div>
        </div>

        {/* Registration Form */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/10 p-6 shadow-2xl">
          <form onSubmit={handleSubmit}>
            {renderStep()}

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-8">
              {currentStep > 1 && (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={handlePrevious}
                  className="flex-1 mr-2"
                >
                  Previous
                </Button>
              )}

              {currentStep < 3 ? (
                <Button
                  type="button"
                  variant="primary"
                  onClick={handleNext}
                  className={`flex-1 ${currentStep > 1 ? "ml-2" : ""}`}
                >
                  Next
                </Button>
              ) : (
                <Button
                  type="submit"
                  variant="primary"
                  loading={isSubmitting}
                  className={`flex-1 ${
                    currentStep > 1 ? "ml-2" : ""
                  } bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700`}
                >
                  <UserPlus className="h-5 w-5 mr-2" />
                  Create Account
                </Button>
              )}
            </div>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-400">
              Already have an account?{" "}
              <Link
                to="/login"
                className="font-medium text-blue-400 hover:text-blue-300 transition-colors"
              >
                Sign in here
              </Link>
            </p>
          </div>

          {/* Lecturer Registration Link */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">
              Are you a lecturer?{" "}
              <Link
                to="/register/lecturer"
                className="text-blue-400 hover:text-blue-300 transition-colors"
              >
                Register as lecturer
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentRegister;
