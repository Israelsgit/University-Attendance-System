import React, { useState } from "react";
import { Plus, X } from "lucide-react";
import Button from "../common/Button";
import Input from "../common/Input";
import Select from "../common/Select";

const CreateCourseModal = ({ isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    course_code: "",
    course_title: "",
    course_units: "",
    semester: "",
    academic_session: "",
    level: "",
    class_days: [],
    start_time: "",
    end_time: "",
    classroom: "",
    max_students: "",
    prerequisites: "",
    description: "",
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

  const handleClassDayChange = (day) => {
    setFormData((prev) => ({
      ...prev,
      class_days: prev.class_days.includes(day)
        ? prev.class_days.filter((d) => d !== day)
        : [...prev.class_days, day],
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.course_code)
      newErrors.course_code = "Course code is required";
    if (!formData.course_title)
      newErrors.course_title = "Course title is required";
    if (!formData.course_units)
      newErrors.course_units = "Course units is required";
    if (!formData.semester) newErrors.semester = "Semester is required";
    if (!formData.academic_session)
      newErrors.academic_session = "Academic session is required";
    if (!formData.level) newErrors.level = "Level is required";
    if (formData.class_days.length === 0)
      newErrors.class_days = "Please select at least one class day";
    if (!formData.start_time) newErrors.start_time = "Start time is required";
    if (!formData.end_time) newErrors.end_time = "End time is required";

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
        course_code: "",
        course_title: "",
        course_units: "",
        semester: "",
        academic_session: "",
        level: "",
        class_days: [],
        start_time: "",
        end_time: "",
        classroom: "",
        max_students: "",
        prerequisites: "",
        description: "",
      });
    } catch (error) {
      console.error("Error creating course:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const semesterOptions = [
    { value: "First Semester", label: "First Semester" },
    { value: "Second Semester", label: "Second Semester" },
  ];

  const levelOptions = [
    { value: "100", label: "100 Level" },
    { value: "200", label: "200 Level" },
    { value: "300", label: "300 Level" },
    { value: "400", label: "400 Level" },
    { value: "500", label: "500 Level" },
  ];

  const classDays = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">
            Create New Course
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
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Course Code"
              name="course_code"
              value={formData.course_code}
              onChange={handleChange}
              placeholder="e.g., CSC 438"
              error={errors.course_code}
              required
            />

            <Input
              label="Course Units"
              name="course_units"
              type="number"
              value={formData.course_units}
              onChange={handleChange}
              min="1"
              max="6"
              error={errors.course_units}
              required
            />
          </div>

          <Input
            label="Course Title"
            name="course_title"
            value={formData.course_title}
            onChange={handleChange}
            placeholder="e.g., Web Programming"
            error={errors.course_title}
            required
          />

          {/* Academic Information */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Select
              label="Semester"
              name="semester"
              value={formData.semester}
              onChange={handleChange}
              options={semesterOptions}
              error={errors.semester}
              required
            />

            <Input
              label="Academic Session"
              name="academic_session"
              value={formData.academic_session}
              onChange={handleChange}
              placeholder="2024/2025"
              error={errors.academic_session}
              required
            />

            <Select
              label="Level"
              name="level"
              value={formData.level}
              onChange={handleChange}
              options={levelOptions}
              error={errors.level}
              required
            />
          </div>

          {/* Class Schedule */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Class Days <span className="text-red-400">*</span>
            </label>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
              {classDays.map((day) => (
                <button
                  key={day}
                  type="button"
                  onClick={() => handleClassDayChange(day)}
                  className={`p-2 rounded-lg border text-sm font-medium transition-all ${
                    formData.class_days.includes(day)
                      ? "bg-blue-600 border-blue-500 text-white"
                      : "bg-slate-700 border-slate-600 text-gray-300 hover:bg-slate-600"
                  }`}
                >
                  {day.substr(0, 3)}
                </button>
              ))}
            </div>
            {errors.class_days && (
              <p className="text-red-400 text-sm mt-1">{errors.class_days}</p>
            )}
          </div>

          {/* Time and Location */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Start Time"
              name="start_time"
              type="time"
              value={formData.start_time}
              onChange={handleChange}
              error={errors.start_time}
              required
            />

            <Input
              label="End Time"
              name="end_time"
              type="time"
              value={formData.end_time}
              onChange={handleChange}
              error={errors.end_time}
              required
            />

            <Input
              label="Classroom"
              name="classroom"
              value={formData.classroom}
              onChange={handleChange}
              placeholder="e.g., LT1, Lab A"
            />
          </div>

          {/* Additional Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Max Students"
              name="max_students"
              type="number"
              value={formData.max_students}
              onChange={handleChange}
              min="1"
              placeholder="100"
            />

            <Input
              label="Prerequisites"
              name="prerequisites"
              value={formData.prerequisites}
              onChange={handleChange}
              placeholder="e.g., CSC 201, CSC 301"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Brief description of the course..."
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
            <Button type="button" onClick={onClose} variant="secondary">
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={isSubmitting}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Course
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCourseModal;
