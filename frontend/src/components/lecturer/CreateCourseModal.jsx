import React, { useState } from "react";
import { X, Plus } from "lucide-react";
import Button from "../common/Button";
import Input from "../common/Input";
import Select from "../common/Select";
import Modal from "../common/Modal";
import { useCourses } from "../../hooks/useCourses";

const CreateCourseModal = ({ isOpen, onClose }) => {
  const { createCourse } = useCourses();
  const [formData, setFormData] = useState({
    course_code: "",
    course_title: "",
    course_unit: 3,
    semester: "First Semester",
    academic_session: "2024/2025",
    level: "100",
    class_days: [],
    class_time_start: "",
    class_time_end: "",
    classroom: "",
    description: "",
    prerequisites: "",
    max_students: 100,
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (name === "class_days") {
      const day = value;
      setFormData((prev) => ({
        ...prev,
        class_days: checked
          ? [...prev.class_days, day]
          : prev.class_days.filter((d) => d !== day),
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: type === "number" ? parseInt(value) || 0 : value,
      }));
    }

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

    if (!formData.course_code.trim()) {
      newErrors.course_code = "Course code is required";
    }

    if (!formData.course_title.trim()) {
      newErrors.course_title = "Course title is required";
    }

    if (formData.course_unit < 1 || formData.course_unit > 6) {
      newErrors.course_unit = "Course unit must be between 1 and 6";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);
    try {
      await createCourse(formData);
      onClose();
      // Reset form
      setFormData({
        course_code: "",
        course_title: "",
        course_unit: 3,
        semester: "First Semester",
        academic_session: "2024/2025",
        level: "100",
        class_days: [],
        class_time_start: "",
        class_time_end: "",
        classroom: "",
        description: "",
        prerequisites: "",
        max_students: 100,
      });
    } catch (error) {
      console.error("Error creating course:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const daysOfWeek = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];

  const semesterOptions = [
    { value: "First Semester", label: "First Semester" },
    { value: "Second Semester", label: "Second Semester" },
    { value: "Rain Semester", label: "Rain Semester" },
  ];

  const levelOptions = [
    { value: "100", label: "100 Level" },
    { value: "200", label: "200 Level" },
    { value: "300", label: "300 Level" },
    { value: "400", label: "400 Level" },
    { value: "500", label: "500 Level" },
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Course"
      size="large"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
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
            name="course_unit"
            type="number"
            value={formData.course_unit}
            onChange={handleChange}
            min="1"
            max="6"
            error={errors.course_unit}
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
            required
          />

          <Input
            label="Academic Session"
            name="academic_session"
            value={formData.academic_session}
            onChange={handleChange}
            placeholder="e.g., 2024/2025"
            required
          />

          <Select
            label="Level"
            name="level"
            value={formData.level}
            onChange={handleChange}
            options={levelOptions}
            required
          />
        </div>

        {/* Schedule Information */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Class Days
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {daysOfWeek.map((day) => (
              <label key={day} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  name="class_days"
                  value={day}
                  checked={formData.class_days.includes(day)}
                  onChange={handleChange}
                  className="rounded border-gray-600 bg-gray-700 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-300">{day}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Start Time"
            name="class_time_start"
            type="time"
            value={formData.class_time_start}
            onChange={handleChange}
          />

          <Input
            label="End Time"
            name="class_time_end"
            type="time"
            value={formData.class_time_end}
            onChange={handleChange}
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
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Brief description of the course..."
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" onClick={onClose} variant="secondary">
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={isLoading}
            className="flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                Create Course
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateCourseModal;
