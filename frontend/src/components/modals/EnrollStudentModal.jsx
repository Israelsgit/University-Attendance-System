import React, { useState } from "react";
import { UserPlus, Search, X, AlertCircle } from "lucide-react";
import Button from "../common/Button";
import Input from "../common/Input";
import Select from "../common/Select";

const EnrollStudentModal = ({
  isOpen,
  onClose,
  onSubmit,
  courses,
  selectedCourse,
}) => {
  const [formData, setFormData] = useState({
    student_email: "",
    course_id: selectedCourse?.id || "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
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

    if (!formData.student_email) {
      newErrors.student_email = "Student email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.student_email)) {
      newErrors.student_email = "Please enter a valid email";
    } else if (
      !formData.student_email.includes("@student.bowen.edu.ng") &&
      !formData.student_email.includes("@bowen.edu.ng")
    ) {
      newErrors.student_email = "Please use a university email address";
    }

    if (!formData.course_id) {
      newErrors.course_id = "Please select a course";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      setFormData({
        student_email: "",
        course_id: selectedCourse?.id || "",
      });
    } catch (error) {
      console.error("Error enrolling student:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const courseOptions = courses.map((course) => ({
    value: course.id,
    label: `${course.course_code} - ${course.course_title}`,
  }));

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">
            Enroll Student in Course
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="space-y-4">
            <Input
              label="Student Email"
              name="student_email"
              type="email"
              value={formData.student_email}
              onChange={handleChange}
              placeholder="student@student.bowen.edu.ng"
              error={errors.student_email}
              required
              icon={Search}
            />

            <Select
              label="Course"
              name="course_id"
              value={formData.course_id}
              onChange={handleChange}
              options={courseOptions}
              placeholder="Select a course"
              error={errors.course_id}
              required
              disabled={!!selectedCourse}
            />
          </div>

          {/* Information Note */}
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <p className="text-blue-400 text-sm font-medium">Note</p>
                <p className="text-blue-300 text-sm mt-1">
                  Make sure the student email is correct. The student will be
                  notified of their enrollment and can then register their face
                  for attendance.
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <Button type="button" onClick={onClose} variant="secondary">
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={isSubmitting}
              className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Enroll Student
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EnrollStudentModal;
