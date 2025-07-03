import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Eye,
  EyeOff,
  UserPlus,
  GraduationCap,
  Upload,
  X,
  Users,
  UserCheck,
  Calendar,
} from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import Button from "../../components/common/Button";
import Input from "../../components/common/Input";

const Register = () => {
  const { register, isAuthenticating } = useAuth();
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    confirmPassword: "",
    phone: "",
    gender: "",
    date_of_birth: "",
    address: "",
    college: "",
    department: "",
    programme: "",
    level: "",
    matric_number: "",
    role: "student", // Default to student registration
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // University-specific data (from Bowen University official structure)
  const colleges = [
    "College of Computing and Communication Studies",
    "College of Agriculture and Engineering Sciences",
    "College of Health Sciences",
    "College of Social and Management Sciences",
    "College of Law",
    "College of Liberal Studies",
    "College of Environmental Sciences",
  ];

  const departments = {
    "College of Computing and Communication Studies": [
      "Computer Science",
      "Information Technology",
      "Cyber Security",
      "Software Engineering",
      "Communication Arts",
      "Mass Communication",
    ],
    "College of Agriculture and Engineering Sciences": [
      "Electrical and Electronics Engineering",
      "Mechatronics Engineering",
      "Chemistry and Industrial Chemistry",
      "Food Science and Technology",
      "Mathematics and Statistics",
      "Physics and Solar Energy",
    ],
    "College of Health Sciences": [
      "Anatomy",
      "Physiotherapy",
      "Medical Laboratory Science",
      "Medicine and Surgery",
      "Nursing Science",
      "Nutrition and Dietetics",
      "Public Health",
    ],
    "College of Social and Management Sciences": [
      "Accounting & Finance",
      "Political Science",
      "Business Administration",
      "Industrial Relations & Personnel Management",
      "International Relations",
      "Sociology",
    ],
    "College of Law": ["Law"],
    "College of Environmental Sciences": [
      "Architecture",
      "Surveying and Geoinformatics",
    ],
    "College of Liberal Studies": [
      "English Language",
      "History and International Studies",
      "Philosophy and Religious Studies",
      "Music",
      "Theatre Arts",
    ],
  };

  const studentLevels = ["100", "200", "300", "400", "500"];
  const genderOptions = ["Male", "Female"];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Reset department when college changes
    if (name === "college") {
      setFormData((prev) => ({
        ...prev,
        college: value,
        department: "",
      }));
    }

    // Auto-generate matric number when department and level change
    if (
      (name === "department" || name === "level") &&
      formData.department &&
      formData.level
    ) {
      generateMatricNumber();
    }

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const generateMatricNumber = () => {
    if (!formData.department || !formData.level) return;

    // Generate department code
    const deptCodes = {
      "Computer Science": "CSC",
      "Information Technology": "IFT",
      "Cyber Security": "CYS",
      "Software Engineering": "SWE",
      "Communication Arts": "COM",
      "Mass Communication": "MCM",
      "Electrical and Electronics Engineering": "EEE",
      "Mechatronics Engineering": "MEC",
      "Chemistry and Industrial Chemistry": "CHM",
      "Food Science and Technology": "FST",
      "Mathematics and Statistics": "MAT",
      "Physics and Solar Energy": "PHY",
      "Medicine and Surgery": "MED",
      "Nursing Science": "NUR",
      "Public Health": "PHC",
      "Medical Laboratory Science": "MLS",
      Physiotherapy: "PHT",
      "Nutrition and Dietetics": "NUT",
      Anatomy: "ANA",
      "Accounting & Finance": "ACC",
      "Political Science": "POL",
      "Business Administration": "BUS",
      "Industrial Relations & Personnel Management": "IRP",
      "International Relations": "INT",
      Sociology: "SOC",
      Law: "LAW",
      Architecture: "ARC",
      "Surveying and Geoinformatics": "SUR",
      "English Language": "ENG",
      "History and International Studies": "HIS",
      "Philosophy and Religious Studies": "PHL",
      Music: "MUS",
      "Theatre Arts": "THR",
    };

    const deptCode = deptCodes[formData.department] || "GEN";
    const currentYear = new Date().getFullYear().toString().slice(-2);

    // Format: BU/DEPT/YY/XXXX (XXXX will be filled by backend)
    const matricBase = `BU/${deptCode}/${currentYear}/`;

    setFormData((prev) => ({
      ...prev,
      matric_number: matricBase + "XXXX", // Backend will replace XXXX with actual number
    }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type and size
      if (!file.type.startsWith("image/")) {
        setErrors((prev) => ({
          ...prev,
          profileImage: "Please select a valid image file",
        }));
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        // 5MB limit
        setErrors((prev) => ({
          ...prev,
          profileImage: "Image file must be less than 5MB",
        }));
        return;
      }

      setProfileImage(file);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);

      // Clear any previous error
      setErrors((prev) => ({ ...prev, profileImage: "" }));
    }
  };

  const removeImage = () => {
    setProfileImage(null);
    setImagePreview(null);
    // Clear file input
    const fileInput = document.getElementById("profileImage");
    if (fileInput) fileInput.value = "";
  };

  const validateForm = () => {
    const newErrors = {};

    // Basic validations
    if (!formData.full_name.trim()) {
      newErrors.full_name = "Full name is required";
    } else if (formData.full_name.trim().length < 2) {
      newErrors.full_name = "Name must be at least 2 characters";
    }

    if (!formData.email) {
      newErrors.email = "Email address is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.college) {
      newErrors.college = "Please select a college";
    }

    if (!formData.department) {
      newErrors.department = "Please select a department";
    }

    if (!formData.programme.trim()) {
      newErrors.programme = "Programme is required";
    }

    if (!formData.level) {
      newErrors.level = "Please select your current level";
    }

    if (!formData.gender) {
      newErrors.gender = "Please select your gender";
    }

    if (!formData.date_of_birth) {
      newErrors.date_of_birth = "Date of birth is required";
    } else {
      const birthDate = new Date(formData.date_of_birth);
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      if (age < 16 || age > 60) {
        newErrors.date_of_birth = "Age must be between 16 and 60 years";
      }
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password =
        "Password must contain uppercase, lowercase, and number";
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    if (formData.phone && !/^[\+]?[\d\s\-\(\)]{10,}$/.test(formData.phone)) {
      newErrors.phone = "Please enter a valid phone number";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    const userData = {
      ...formData,
      profileImage,
      university: "Bowen University", // Auto-set
    };

    const result = await register(userData);
    if (!result.success) {
      // Error is already handled by the context and toast
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-20 w-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-2xl">
            <Users className="h-10 w-10 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">
            Student Registration
          </h2>
          <p className="text-gray-300">Bowen University Attendance System</p>
          <p className="text-sm text-gray-400 mt-2">
            Create your student account to access attendance tracking
          </p>
        </div>

        {/* Registration Form */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-glass border border-white/20 p-8">
          <form className="space-y-8" onSubmit={handleSubmit}>
            {/* Profile Image Upload */}
            <div className="flex flex-col items-center">
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Profile Photo
              </label>
              <div className="relative">
                <div className="h-32 w-32 rounded-full bg-gradient-to-r from-green-500 to-blue-600 flex items-center justify-center overflow-hidden">
                  {imagePreview ? (
                    <img
                      src={imagePreview}
                      alt="Profile preview"
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <Users className="h-12 w-12 text-white" />
                  )}
                </div>

                {imagePreview ? (
                  <button
                    type="button"
                    onClick={removeImage}
                    className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                ) : (
                  <label
                    htmlFor="profileImage"
                    className="absolute -bottom-2 -right-2 bg-blue-500 hover:bg-blue-600 text-white rounded-full p-2 cursor-pointer transition-colors"
                  >
                    <Upload className="h-4 w-4" />
                  </label>
                )}

                <input
                  id="profileImage"
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="hidden"
                />
              </div>
              {errors.profileImage && (
                <p className="mt-2 text-sm text-red-400">
                  {errors.profileImage}
                </p>
              )}
              <p className="mt-2 text-xs text-gray-400 text-center">
                Upload a clear photo for face recognition • Max 5MB
              </p>
            </div>

            {/* Personal Information */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Personal Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  label="Full Name"
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  error={errors.full_name}
                  placeholder="Enter your full name as on official documents"
                  required
                />

                <Input
                  label="Email Address"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  error={errors.email}
                  placeholder="yourname@student.bowen.edu.ng"
                  required
                />

                <Input
                  label="Phone Number"
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  error={errors.phone}
                  placeholder="+234 000 000 0000"
                />

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Gender *
                  </label>
                  <select
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    required
                  >
                    <option value="">Select Gender</option>
                    {genderOptions.map((gender) => (
                      <option
                        key={gender}
                        value={gender}
                        className="bg-slate-800"
                      >
                        {gender}
                      </option>
                    ))}
                  </select>
                  {errors.gender && (
                    <p className="mt-1 text-sm text-red-400">{errors.gender}</p>
                  )}
                </div>

                <Input
                  label="Date of Birth"
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  error={errors.date_of_birth}
                  required
                />

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Address
                  </label>
                  <textarea
                    name="address"
                    rows={3}
                    value={formData.address}
                    onChange={handleChange}
                    placeholder="Enter your residential address"
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                  />
                </div>
              </div>
            </div>

            {/* Academic Information */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <GraduationCap className="h-5 w-5 mr-2" />
                Academic Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    College *
                  </label>
                  <select
                    name="college"
                    value={formData.college}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    required
                  >
                    <option value="">Select College</option>
                    {colleges.map((college) => (
                      <option
                        key={college}
                        value={college}
                        className="bg-slate-800"
                      >
                        {college}
                      </option>
                    ))}
                  </select>
                  {errors.college && (
                    <p className="mt-1 text-sm text-red-400">
                      {errors.college}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Department *
                  </label>
                  <select
                    name="department"
                    value={formData.department}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:opacity-50"
                    required
                    disabled={!formData.college}
                  >
                    <option value="">Select Department</option>
                    {formData.college &&
                      departments[formData.college]?.map((dept) => (
                        <option
                          key={dept}
                          value={dept}
                          className="bg-slate-800"
                        >
                          {dept}
                        </option>
                      ))}
                  </select>
                  {errors.department && (
                    <p className="mt-1 text-sm text-red-400">
                      {errors.department}
                    </p>
                  )}
                </div>

                <Input
                  label="Programme"
                  type="text"
                  name="programme"
                  value={formData.programme}
                  onChange={handleChange}
                  error={errors.programme}
                  placeholder="e.g., Computer Science, Information Technology"
                  required
                />

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Current Level *
                  </label>
                  <select
                    name="level"
                    value={formData.level}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    required
                  >
                    <option value="">Select Level</option>
                    {studentLevels.map((level) => (
                      <option
                        key={level}
                        value={level}
                        className="bg-slate-800"
                      >
                        {level} Level
                      </option>
                    ))}
                  </select>
                  {errors.level && (
                    <p className="mt-1 text-sm text-red-400">{errors.level}</p>
                  )}
                </div>

                {/* Auto-generated Matric Number */}
                {formData.matric_number && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Matric Number (Auto-generated)
                    </label>
                    <div className="w-full px-3 py-2 bg-green-500/10 border border-green-500/20 rounded-lg text-green-300">
                      {formData.matric_number}
                    </div>
                    <p className="mt-1 text-xs text-gray-400">
                      This will be finalized during registration approval
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Security Information */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <UserCheck className="h-5 w-5 mr-2" />
                Security Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="relative">
                  <Input
                    label="Password"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    error={errors.password}
                    placeholder="Create a strong password"
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

                <div className="relative">
                  <Input
                    label="Confirm Password"
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    error={errors.confirmPassword}
                    placeholder="Confirm your password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-9 text-gray-400 hover:text-white transition-colors"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              <div className="mt-4 p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                <h4 className="text-sm font-semibold text-yellow-200 mb-2">
                  Password Requirements:
                </h4>
                <ul className="text-xs text-yellow-200 space-y-1">
                  <li>• At least 8 characters long</li>
                  <li>• Contains uppercase and lowercase letters</li>
                  <li>• Contains at least one number</li>
                  <li>• Remember this password - you'll need it to login</li>
                </ul>
              </div>
            </div>

            {/* Terms and Conditions */}
            <div className="flex items-start">
              <input
                id="terms"
                name="terms"
                type="checkbox"
                required
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded bg-white/10 border-white/20 mt-1"
              />
              <label
                htmlFor="terms"
                className="ml-3 block text-sm text-gray-300"
              >
                I agree to the{" "}
                <a href="#" className="text-blue-400 hover:text-blue-300">
                  Terms of Service
                </a>{" "}
                and{" "}
                <a href="#" className="text-blue-400 hover:text-blue-300">
                  Privacy Policy
                </a>{" "}
                of Bowen University Attendance System. I understand that my
                biometric data (face recognition) will be used for attendance
                tracking purposes only.
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="large"
              fullWidth
              loading={isAuthenticating}
              className="group bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
            >
              <UserPlus className="h-5 w-5 mr-2 group-hover:scale-110 transition-transform" />
              Register as Student
            </Button>
          </form>

          {/* Registration Process Info */}
          <div className="mt-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
            <h4 className="text-sm font-semibold text-blue-200 mb-2">
              Registration Process:
            </h4>
            <ol className="text-xs text-blue-200 space-y-1 list-decimal list-inside">
              <li>Complete this registration form with accurate information</li>
              <li>
                Your account will be reviewed and approved by the admissions
                office
              </li>
              <li>
                Visit your lecturer to register your face for attendance
                tracking
              </li>
              <li>
                Start attending classes - your attendance will be automatically
                tracked!
              </li>
            </ol>
          </div>

          {/* Sign in link */}
          <p className="mt-6 text-center text-sm text-gray-400">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-medium text-blue-400 hover:text-blue-300 transition-colors"
            >
              Sign in here
            </Link>
          </p>

          {/* Staff registration note */}
          <div className="mt-4 p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
            <p className="text-xs text-purple-200 text-center">
              <strong>Lecturers and Admin staff:</strong> Your accounts are
              created by the IT department. Please contact the system
              administrator if you need access.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
