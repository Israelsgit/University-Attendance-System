import React, { useState } from "react";
import { User, Camera, Save, Lock, Shield } from "lucide-react";
import { toast } from "react-hot-toast";

import { useAuth } from "../hooks/useAuth";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import FaceRegistrationModal from "../components/modals/FaceRegisterationModal";

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [showFaceRegistration, setShowFaceRegistration] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || "",
    phone: user?.phone || "",
    address: user?.address || "",
    gender: user?.gender || "",
  });
  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSaveProfile = async () => {
    try {
      // Mock update - replace with actual API call
      await updateUser(formData);
      toast.success("Profile updated successfully!");
      setIsEditing(false);
    } catch (error) {
      toast.error("Failed to update profile");
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error("Passwords do not match");
      return;
    }

    if (passwordData.new_password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    try {
      // Mock password change - replace with actual API call
      toast.success("Password changed successfully!");
      setIsChangingPassword(false);
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (error) {
      toast.error("Failed to change password");
    }
  };

  const handleFaceRegistrationSuccess = () => {
    setShowFaceRegistration(false);
    toast.success("Face registered successfully!");
    // Update user data if needed
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <User className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Please log in to view your profile.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
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
          {/* Profile Overview */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="text-center">
              <div className="w-24 h-24 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">
                  {user.full_name?.charAt(0).toUpperCase()}
                </span>
              </div>

              <h2 className="text-xl font-semibold text-white mb-1">
                {user.full_name}
              </h2>
              <div className="flex items-center justify-center mb-2">
                {user.role === "lecturer" && (
                  <Shield className="h-4 w-4 text-purple-400 mr-1" />
                )}
                <span className="text-sm text-gray-400 capitalize">
                  {user.role}
                </span>
              </div>

              <p className="text-sm text-gray-500">{user.email}</p>

              {user.role === "student" && user.matric_number && (
                <p className="text-xs text-gray-600 mt-1">
                  {user.matric_number}
                </p>
              )}

              {user.role === "lecturer" && user.staff_id && (
                <p className="text-xs text-gray-600 mt-1">{user.staff_id}</p>
              )}

              {/* Face Registration Status */}
              <div className="mt-4 p-3 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Face Registration</span>
                  {user.is_face_registered ? (
                    <span className="text-green-400">✓ Registered</span>
                  ) : (
                    <span className="text-yellow-400">Not Registered</span>
                  )}
                </div>

                {!user.is_face_registered && (
                  <Button
                    onClick={() => setShowFaceRegistration(true)}
                    variant="primary"
                    size="small"
                    className="w-full mt-2"
                  >
                    <Camera className="h-3 w-3 mr-1" />
                    Register Face
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">
                  Personal Information
                </h3>
                <Button
                  onClick={() => setIsEditing(!isEditing)}
                  variant="secondary"
                  size="small"
                >
                  {isEditing ? "Cancel" : "Edit"}
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                />

                <Input label="Email Address" value={user.email} disabled />

                <Input
                  label="Phone Number"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  placeholder="Enter phone number"
                />

                <Input
                  label="Gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  placeholder="Enter gender"
                />

                <div className="md:col-span-2">
                  <Input
                    label="Address"
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    placeholder="Enter address"
                  />
                </div>
              </div>

              {isEditing && (
                <div className="flex gap-3 mt-6">
                  <Button onClick={handleSaveProfile} variant="primary">
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                  <Button
                    onClick={() => setIsEditing(false)}
                    variant="secondary"
                  >
                    Cancel
                  </Button>
                </div>
              )}
            </div>

            {/* Academic Information */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold text-white mb-6">
                Academic Information
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="University" value={user.university} disabled />

                <Input label="College" value={user.college} disabled />

                <Input label="Department" value={user.department} disabled />

                <Input
                  label="Programme"
                  value={user.programme || "N/A"}
                  disabled
                />

                {user.role === "student" && (
                  <>
                    <Input
                      label="Level"
                      value={user.level ? `${user.level} Level` : "N/A"}
                      disabled
                    />

                    <Input
                      label="Matriculation Number"
                      value={user.matric_number}
                      disabled
                    />
                  </>
                )}

                {user.role === "lecturer" && (
                  <Input label="Staff ID" value={user.staff_id} disabled />
                )}
              </div>
            </div>

            {/* Security */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">Security</h3>
                <Button
                  onClick={() => setIsChangingPassword(!isChangingPassword)}
                  variant="secondary"
                  size="small"
                >
                  <Lock className="h-3 w-3 mr-1" />
                  {isChangingPassword ? "Cancel" : "Change Password"}
                </Button>
              </div>

              {isChangingPassword && (
                <div className="space-y-4">
                  <Input
                    label="Current Password"
                    name="current_password"
                    type="password"
                    value={passwordData.current_password}
                    onChange={handlePasswordChange}
                    placeholder="Enter current password"
                  />

                  <Input
                    label="New Password"
                    name="new_password"
                    type="password"
                    value={passwordData.new_password}
                    onChange={handlePasswordChange}
                    placeholder="Enter new password"
                  />

                  <Input
                    label="Confirm New Password"
                    name="confirm_password"
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={handlePasswordChange}
                    placeholder="Confirm new password"
                  />

                  <div className="flex gap-3">
                    <Button onClick={handleChangePassword} variant="primary">
                      Change Password
                    </Button>
                    <Button
                      onClick={() => setIsChangingPassword(false)}
                      variant="secondary"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}

              {!isChangingPassword && (
                <p className="text-gray-400 text-sm">
                  Keep your account secure by using a strong password and
                  changing it regularly.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Face Registration Modal */}
      {showFaceRegistration && (
        <FaceRegistrationModal
          isOpen={showFaceRegistration}
          onClose={() => setShowFaceRegistration(false)}
          onSuccess={handleFaceRegistrationSuccess}
        />
      )}
    </div>
  );
};

export default Profile;
