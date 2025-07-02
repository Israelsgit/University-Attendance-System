import React, { useState } from "react";
import {
  User,
  Mail,
  Building,
  IdCard,
  Camera,
  Edit3,
  Save,
  X,
  Lock,
  Eye,
  EyeOff,
  Upload,
  Calendar,
  Clock,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useAttendance } from "../hooks/useAttendance";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import Modal from "../components/common/Modal";
import { format } from "date-fns";

const Profile = () => {
  const { user, updateProfile, uploadProfileImage, changePassword } = useAuth();
  const { weeklyStats } = useAttendance();

  const [isEditing, setIsEditing] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  const [profileData, setProfileData] = useState({
    name: user?.name || "",
    email: user?.email || "",
    department: user?.department || "",
    employeeId: user?.employeeId || "",
    phone: user?.phone || "",
    bio: user?.bio || "",
  });
  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [errors, setErrors] = useState({});
  const [isUpdating, setIsUpdating] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({
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

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({
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

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        // 5MB limit
        setErrors({ image: "Image must be less than 5MB" });
        return;
      }

      if (!file.type.startsWith("image/")) {
        setErrors({ image: "Please select a valid image file" });
        return;
      }

      setSelectedImage(file);

      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);

      setErrors({});
    }
  };

  const validateProfile = () => {
    const newErrors = {};

    if (!profileData.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!profileData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(profileData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!profileData.department.trim()) {
      newErrors.department = "Department is required";
    }

    if (!profileData.employeeId.trim()) {
      newErrors.employeeId = "Employee ID is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validatePassword = () => {
    const newErrors = {};

    if (!passwordData.currentPassword) {
      newErrors.currentPassword = "Current password is required";
    }

    if (!passwordData.newPassword) {
      newErrors.newPassword = "New password is required";
    } else if (passwordData.newPassword.length < 6) {
      newErrors.newPassword = "Password must be at least 6 characters";
    }

    if (!passwordData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your new password";
    } else if (passwordData.newPassword !== passwordData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSaveProfile = async () => {
    if (!validateProfile()) return;

    setIsUpdating(true);
    const result = await updateProfile(profileData);
    if (result.success) {
      setIsEditing(false);
    }
    setIsUpdating(false);
  };

  const handleCancelEdit = () => {
    setProfileData({
      name: user?.name || "",
      email: user?.email || "",
      department: user?.department || "",
      employeeId: user?.employeeId || "",
      phone: user?.phone || "",
      bio: user?.bio || "",
    });
    setIsEditing(false);
    setErrors({});
  };

  const handlePasswordSubmit = async () => {
    if (!validatePassword()) return;

    setIsUpdating(true);
    const result = await changePassword(passwordData);
    if (result.success) {
      setShowPasswordModal(false);
      setPasswordData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    }
    setIsUpdating(false);
  };

  const handleImageUpload = async () => {
    if (!selectedImage) return;

    setIsUpdating(true);
    const result = await uploadProfileImage(selectedImage);
    if (result.success) {
      setShowImageModal(false);
      setSelectedImage(null);
      setImagePreview(null);
    }
    setIsUpdating(false);
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const profileStats = [
    {
      label: "Total Working Days",
      value: weeklyStats?.totalDays || 0,
      icon: Calendar,
    },
    {
      label: "Average Hours/Day",
      value: `${weeklyStats?.avgHours || 0}h`,
      icon: Clock,
    },
    {
      label: "This Month",
      value: `${weeklyStats?.monthlyAttendance || 0}%`,
      icon: Calendar,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Profile Settings
          </h1>
          <p className="text-gray-400">
            Manage your account information and preferences
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Card */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 sticky top-6">
              {/* Profile Image */}
              <div className="text-center mb-6">
                <div className="relative inline-block">
                  <div className="h-32 w-32 rounded-full bg-gradient-to-r from-primary-500 to-purple-600 flex items-center justify-center overflow-hidden mx-auto">
                    {user?.profileImage ? (
                      <img
                        src={user.profileImage}
                        alt={user.name}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <User className="h-16 w-16 text-white" />
                    )}
                  </div>
                  <button
                    onClick={() => setShowImageModal(true)}
                    className="absolute bottom-0 right-0 h-10 w-10 bg-primary-600 rounded-full flex items-center justify-center text-white hover:bg-primary-700 transition-colors shadow-lg"
                  >
                    <Camera className="h-5 w-5" />
                  </button>
                </div>
                <h2 className="text-xl font-bold text-white mt-4">
                  {user?.name}
                </h2>
                <p className="text-gray-400">{user?.department}</p>
                <p className="text-sm text-gray-500">ID: {user?.employeeId}</p>
              </div>

              {/* Profile Stats */}
              <div className="space-y-4">
                {profileStats.map((stat, index) => {
                  const IconComponent = stat.icon;
                  return (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-white/5 rounded-lg"
                    >
                      <div className="flex items-center">
                        <IconComponent className="h-5 w-5 text-primary-400 mr-3" />
                        <span className="text-gray-300 text-sm">
                          {stat.label}
                        </span>
                      </div>
                      <span className="text-white font-semibold">
                        {stat.value}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Quick Actions */}
              <div className="mt-6 space-y-3">
                <Button
                  onClick={() => setShowPasswordModal(true)}
                  variant="secondary"
                  fullWidth
                  className="justify-center"
                >
                  <Lock className="h-4 w-4 mr-2" />
                  Change Password
                </Button>
              </div>
            </div>
          </div>

          {/* Profile Form */}
          <div className="lg:col-span-2">
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">
                  Personal Information
                </h3>
                {!isEditing ? (
                  <Button
                    onClick={() => setIsEditing(true)}
                    variant="secondary"
                    size="small"
                  >
                    <Edit3 className="h-4 w-4 mr-2" />
                    Edit
                  </Button>
                ) : (
                  <div className="flex space-x-3">
                    <Button
                      onClick={handleCancelEdit}
                      variant="secondary"
                      size="small"
                    >
                      <X className="h-4 w-4 mr-2" />
                      Cancel
                    </Button>
                    <Button
                      onClick={handleSaveProfile}
                      variant="primary"
                      size="small"
                      loading={isUpdating}
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Save
                    </Button>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  label="Full Name"
                  name="name"
                  value={profileData.name}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  error={errors.name}
                  icon={User}
                />

                <Input
                  label="Email Address"
                  name="email"
                  type="email"
                  value={profileData.email}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  error={errors.email}
                  icon={Mail}
                />

                <Input
                  label="Employee ID"
                  name="employeeId"
                  value={profileData.employeeId}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  error={errors.employeeId}
                  icon={IdCard}
                />

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Department
                  </label>
                  <div className="relative">
                    <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <select
                      name="department"
                      value={profileData.department}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className="w-full pl-10 pr-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <option value="Engineering" className="bg-gray-800">
                        Engineering
                      </option>
                      <option value="Marketing" className="bg-gray-800">
                        Marketing
                      </option>
                      <option value="Sales" className="bg-gray-800">
                        Sales
                      </option>
                      <option value="HR" className="bg-gray-800">
                        Human Resources
                      </option>
                      <option value="Finance" className="bg-gray-800">
                        Finance
                      </option>
                      <option value="Operations" className="bg-gray-800">
                        Operations
                      </option>
                      <option value="IT" className="bg-gray-800">
                        Information Technology
                      </option>
                    </select>
                  </div>
                  {errors.department && (
                    <p className="mt-1 text-sm text-red-400">
                      {errors.department}
                    </p>
                  )}
                </div>

                <Input
                  label="Phone Number"
                  name="phone"
                  value={profileData.phone}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  placeholder="Enter your phone number"
                />

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Bio
                  </label>
                  <textarea
                    name="bio"
                    rows={4}
                    value={profileData.bio}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    placeholder="Tell us about yourself..."
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed resize-none"
                  />
                </div>
              </div>

              {/* Account Information */}
              <div className="mt-8 pt-8 border-t border-white/20">
                <h4 className="text-lg font-semibold text-white mb-4">
                  Account Information
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-4 bg-white/5 rounded-lg">
                    <p className="text-sm text-gray-400">Member Since</p>
                    <p className="text-white font-semibold">
                      {user?.createdAt
                        ? format(new Date(user.createdAt), "MMMM yyyy")
                        : "N/A"}
                    </p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg">
                    <p className="text-sm text-gray-400">Last Login</p>
                    <p className="text-white font-semibold">
                      {user?.lastLogin
                        ? format(new Date(user.lastLogin), "MMM dd, yyyy HH:mm")
                        : "N/A"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Change Password Modal */}
      <Modal
        isOpen={showPasswordModal}
        onClose={() => setShowPasswordModal(false)}
        title="Change Password"
        maxWidth="md"
      >
        <div className="space-y-6">
          <div className="relative">
            <Input
              label="Current Password"
              type={showPasswords.current ? "text" : "password"}
              name="currentPassword"
              value={passwordData.currentPassword}
              onChange={handlePasswordChange}
              error={errors.currentPassword}
              placeholder="Enter your current password"
            />
            <button
              type="button"
              className="absolute right-3 top-9 text-gray-400 hover:text-white transition-colors"
              onClick={() => togglePasswordVisibility("current")}
            >
              {showPasswords.current ? (
                <EyeOff className="h-5 w-5" />
              ) : (
                <Eye className="h-5 w-5" />
              )}
            </button>
          </div>

          <div className="relative">
            <Input
              label="New Password"
              type={showPasswords.new ? "text" : "password"}
              name="newPassword"
              value={passwordData.newPassword}
              onChange={handlePasswordChange}
              error={errors.newPassword}
              placeholder="Enter your new password"
            />
            <button
              type="button"
              className="absolute right-3 top-9 text-gray-400 hover:text-white transition-colors"
              onClick={() => togglePasswordVisibility("new")}
            >
              {showPasswords.new ? (
                <EyeOff className="h-5 w-5" />
              ) : (
                <Eye className="h-5 w-5" />
              )}
            </button>
          </div>

          <div className="relative">
            <Input
              label="Confirm New Password"
              type={showPasswords.confirm ? "text" : "password"}
              name="confirmPassword"
              value={passwordData.confirmPassword}
              onChange={handlePasswordChange}
              error={errors.confirmPassword}
              placeholder="Confirm your new password"
            />
            <button
              type="button"
              className="absolute right-3 top-9 text-gray-400 hover:text-white transition-colors"
              onClick={() => togglePasswordVisibility("confirm")}
            >
              {showPasswords.confirm ? (
                <EyeOff className="h-5 w-5" />
              ) : (
                <Eye className="h-5 w-5" />
              )}
            </button>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              onClick={() => setShowPasswordModal(false)}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={handlePasswordSubmit}
              variant="primary"
              loading={isUpdating}
            >
              Update Password
            </Button>
          </div>
        </div>
      </Modal>

      {/* Profile Image Modal */}
      <Modal
        isOpen={showImageModal}
        onClose={() => setShowImageModal(false)}
        title="Update Profile Picture"
        maxWidth="md"
      >
        <div className="space-y-6">
          {/* Image Preview */}
          <div className="text-center">
            <div className="h-40 w-40 rounded-full bg-gradient-to-r from-primary-500 to-purple-600 flex items-center justify-center overflow-hidden mx-auto">
              {imagePreview ? (
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="h-full w-full object-cover"
                />
              ) : user?.profileImage ? (
                <img
                  src={user.profileImage}
                  alt={user.name}
                  className="h-full w-full object-cover"
                />
              ) : (
                <User className="h-20 w-20 text-white" />
              )}
            </div>
          </div>

          {/* File Upload */}
          <div>
            <label
              htmlFor="profile-image-upload"
              className="block w-full cursor-pointer border-2 border-dashed border-white/20 rounded-lg p-6 text-center hover:border-white/40 transition-colors"
            >
              <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-300">Click to upload a new image</p>
              <p className="text-sm text-gray-400 mt-1">PNG, JPG up to 5MB</p>
            </label>
            <input
              id="profile-image-upload"
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="hidden"
            />
            {errors.image && (
              <p className="mt-2 text-sm text-red-400">{errors.image}</p>
            )}
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              onClick={() => {
                setShowImageModal(false);
                setSelectedImage(null);
                setImagePreview(null);
                setErrors({});
              }}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={handleImageUpload}
              variant="primary"
              loading={isUpdating}
              disabled={!selectedImage}
            >
              Update Picture
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Profile;
