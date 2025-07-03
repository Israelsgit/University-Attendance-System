import React, { useState, useEffect } from "react";
import {
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Camera,
  Edit,
  Save,
  X,
  Check,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import Button from "../components/common/Button";
import Card from "../components/common/Card";
import Input from "../components/common/Input";
import Modal from "../components/common/Modal";
import toast from "react-hot-toast";

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [showFaceRegistration, setShowFaceRegistration] = useState(false);
  const [formData, setFormData] = useState({
    full_name: "",
    phone: "",
    address: "",
    gender: "",
  });

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || "",
        phone: user.phone || "",
        address: user.address || "",
        gender: user.gender || "",
      });
    }
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    try {
      await updateProfile(formData);
      setIsEditing(false);
      toast.success("Profile updated successfully!");
    } catch (error) {
      toast.error("Failed to update profile");
    }
  };

  const handleCancel = () => {
    setFormData({
      full_name: user.full_name || "",
      phone: user.phone || "",
      address: user.address || "",
      gender: user.gender || "",
    });
    setIsEditing(false);
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Profile</h1>
          <p className="text-gray-300">Manage your account information</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Picture & Basic Info */}
          <Card className="p-6">
            <div className="text-center">
              <div className="relative inline-block mb-4">
                <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  {user.profile_image ? (
                    <img
                      src={user.profile_image}
                      alt="Profile"
                      className="w-full h-full rounded-full object-cover"
                    />
                  ) : (
                    <User className="h-12 w-12 text-white" />
                  )}
                </div>
                <button className="absolute bottom-0 right-0 bg-blue-600 hover:bg-blue-700 rounded-full p-2 transition-colors">
                  <Camera className="h-4 w-4 text-white" />
                </button>
              </div>

              <h2 className="text-xl font-bold text-white mb-1">
                {user.full_name}
              </h2>
              <p className="text-gray-400 text-sm mb-2">
                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </p>
              <p className="text-gray-500 text-xs">
                {user.student_id || user.staff_id || user.matric_number}
              </p>

              {/* Face Registration Status */}
              <div className="mt-4 p-3 rounded-lg bg-gray-800/50">
                <div className="flex items-center justify-center gap-2 mb-2">
                  {user.is_face_registered ? (
                    <Check className="h-4 w-4 text-green-400" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-yellow-400" />
                  )}
                  <span className="text-sm font-medium text-white">
                    Face Registration
                  </span>
                </div>
                <p
                  className={`text-xs ${
                    user.is_face_registered
                      ? "text-green-400"
                      : "text-yellow-400"
                  }`}
                >
                  {user.is_face_registered ? "Registered" : "Not Registered"}
                </p>

                {!user.is_face_registered && user.role === "student" && (
                  <Button
                    onClick={() => setShowFaceRegistration(true)}
                    size="sm"
                    className="mt-2 w-full"
                    variant="primary"
                  >
                    Register Face
                  </Button>
                )}
              </div>
            </div>
          </Card>

          {/* Personal Information */}
          <Card className="lg:col-span-2 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white">
                Personal Information
              </h3>
              <div className="flex gap-2">
                {isEditing ? (
                  <>
                    <Button onClick={handleSave} size="sm" variant="success">
                      <Save className="h-4 w-4 mr-2" />
                      Save
                    </Button>
                    <Button
                      onClick={handleCancel}
                      size="sm"
                      variant="secondary"
                    >
                      <X className="h-4 w-4 mr-2" />
                      Cancel
                    </Button>
                  </>
                ) : (
                  <Button
                    onClick={() => setIsEditing(true)}
                    size="sm"
                    variant="primary"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </Button>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Full Name
                </label>
                {isEditing ? (
                  <Input
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    placeholder="Enter your full name"
                  />
                ) : (
                  <p className="text-white bg-gray-800/50 p-3 rounded-lg">
                    {user.full_name}
                  </p>
                )}
              </div>

              {/* Email (Read-only) */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email Address
                </label>
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-gray-400" />
                  <p className="text-gray-400 bg-gray-800/30 p-3 rounded-lg flex-1">
                    {user.email}
                  </p>
                </div>
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Phone Number
                </label>
                {isEditing ? (
                  <Input
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="Enter your phone number"
                    icon={Phone}
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    <Phone className="h-4 w-4 text-gray-400" />
                    <p className="text-white bg-gray-800/50 p-3 rounded-lg flex-1">
                      {user.phone || "Not provided"}
                    </p>
                  </div>
                )}
              </div>

              {/* Gender */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Gender
                </label>
                {isEditing ? (
                  <select
                    name="gender"
                    value={formData.gender}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                ) : (
                  <p className="text-white bg-gray-800/50 p-3 rounded-lg">
                    {user.gender || "Not specified"}
                  </p>
                )}
              </div>

              {/* Address */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Address
                </label>
                {isEditing ? (
                  <textarea
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    placeholder="Enter your address"
                    rows="3"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
                  />
                ) : (
                  <div className="flex items-start gap-2">
                    <MapPin className="h-4 w-4 text-gray-400 mt-3" />
                    <p className="text-white bg-gray-800/50 p-3 rounded-lg flex-1">
                      {user.address || "Not provided"}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* Academic/Professional Information */}
        <Card className="mt-6 p-6">
          <h3 className="text-lg font-semibold text-white mb-6">
            {user.role === "student"
              ? "Academic Information"
              : "Professional Information"}
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                University
              </label>
              <p className="text-white bg-gray-800/50 p-3 rounded-lg">
                {user.university}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                College
              </label>
              <p className="text-white bg-gray-800/50 p-3 rounded-lg">
                {user.college}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Department
              </label>
              <p className="text-white bg-gray-800/50 p-3 rounded-lg">
                {user.department}
              </p>
            </div>

            {user.role === "student" && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Programme
                  </label>
                  <p className="text-white bg-gray-800/50 p-3 rounded-lg">
                    {user.programme}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Level
                  </label>
                  <p className="text-white bg-gray-800/50 p-3 rounded-lg">
                    {user.level} Level
                  </p>
                </div>

                {user.admission_date && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Admission Date
                    </label>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <p className="text-white bg-gray-800/50 p-3 rounded-lg flex-1">
                        {new Date(user.admission_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                )}
              </>
            )}

            {(user.role === "lecturer" || user.role === "admin") &&
              user.employment_date && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Employment Date
                  </label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <p className="text-white bg-gray-800/50 p-3 rounded-lg flex-1">
                      {new Date(user.employment_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              )}
          </div>
        </Card>

        {/* Account Status */}
        <Card className="mt-6 p-6">
          <h3 className="text-lg font-semibold text-white mb-6">
            Account Status
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gray-800/50 rounded-lg">
              <div
                className={`inline-flex items-center justify-center w-12 h-12 rounded-full mb-3 ${
                  user.is_active ? "bg-green-500/20" : "bg-red-500/20"
                }`}
              >
                {user.is_active ? (
                  <Check className="h-6 w-6 text-green-400" />
                ) : (
                  <X className="h-6 w-6 text-red-400" />
                )}
              </div>
              <p className="text-sm font-medium text-gray-300">
                Account Status
              </p>
              <p
                className={`text-lg font-bold ${
                  user.is_active ? "text-green-400" : "text-red-400"
                }`}
              >
                {user.is_active ? "Active" : "Inactive"}
              </p>
            </div>

            <div className="text-center p-4 bg-gray-800/50 rounded-lg">
              <div
                className={`inline-flex items-center justify-center w-12 h-12 rounded-full mb-3 ${
                  user.is_verified ? "bg-blue-500/20" : "bg-yellow-500/20"
                }`}
              >
                {user.is_verified ? (
                  <Check className="h-6 w-6 text-blue-400" />
                ) : (
                  <AlertCircle className="h-6 w-6 text-yellow-400" />
                )}
              </div>
              <p className="text-sm font-medium text-gray-300">
                Verification Status
              </p>
              <p
                className={`text-lg font-bold ${
                  user.is_verified ? "text-blue-400" : "text-yellow-400"
                }`}
              >
                {user.is_verified ? "Verified" : "Pending"}
              </p>
            </div>

            <div className="text-center p-4 bg-gray-800/50 rounded-lg">
              <div
                className={`inline-flex items-center justify-center w-12 h-12 rounded-full mb-3 ${
                  user.is_face_registered
                    ? "bg-purple-500/20"
                    : "bg-gray-500/20"
                }`}
              >
                <Camera
                  className={`h-6 w-6 ${
                    user.is_face_registered
                      ? "text-purple-400"
                      : "text-gray-400"
                  }`}
                />
              </div>
              <p className="text-sm font-medium text-gray-300">
                Face Registration
              </p>
              <p
                className={`text-lg font-bold ${
                  user.is_face_registered ? "text-purple-400" : "text-gray-400"
                }`}
              >
                {user.is_face_registered ? "Registered" : "Not Registered"}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Face Registration Modal */}
      {showFaceRegistration && (
        <Modal
          isOpen={showFaceRegistration}
          onClose={() => setShowFaceRegistration(false)}
          title="Face Registration"
        >
          <div className="text-center py-8">
            <Camera className="h-16 w-16 text-blue-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">
              Face Registration Required
            </h3>
            <p className="text-gray-300 mb-6">
              Please visit your lecturer to register your face for attendance
              marking. This process requires in-person verification.
            </p>
            <Button
              onClick={() => setShowFaceRegistration(false)}
              variant="primary"
            >
              Understood
            </Button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Profile;
