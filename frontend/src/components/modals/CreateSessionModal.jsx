import React, { useState } from "react";
import { Camera, X, Clock, Calendar } from "lucide-react";
import Button from "../common/Button";
import Input from "../common/Input";
import Select from "../common/Select";

const CreateSessionModal = ({ isOpen, onClose, onSubmit, course }) => {
  const [formData, setFormData] = useState({
    session_date: new Date().toISOString().split("T")[0],
    session_topic: "",
    session_type: "lecture",
    duration_minutes: "60",
    notes: "",
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

    if (!formData.session_date) {
      newErrors.session_date = "Session date is required";
    }

    if (!formData.session_topic) {
      newErrors.session_topic = "Session topic is required";
    }

    if (!formData.duration_minutes || formData.duration_minutes < 15) {
      newErrors.duration_minutes = "Duration must be at least 15 minutes";
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
        session_date: new Date().toISOString().split("T")[0],
        session_topic: "",
        session_type: "lecture",
        duration_minutes: "60",
        notes: "",
      });
    } catch (error) {
      console.error("Error creating session:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const sessionTypeOptions = [
    { value: "lecture", label: "Lecture" },
    { value: "lab", label: "Laboratory" },
    { value: "tutorial", label: "Tutorial" },
    { value: "seminar", label: "Seminar" },
    { value: "practical", label: "Practical" },
    { value: "exam", label: "Examination" },
    { value: "test", label: "Test/Quiz" },
  ];

  const durationOptions = [
    { value: "30", label: "30 minutes" },
    { value: "45", label: "45 minutes" },
    { value: "60", label: "1 hour" },
    { value: "90", label: "1.5 hours" },
    { value: "120", label: "2 hours" },
    { value: "150", label: "2.5 hours" },
    { value: "180", label: "3 hours" },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 w-full max-w-lg">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <div>
            <h2 className="text-xl font-semibold text-white">
              Start Attendance Session
            </h2>
            {course && (
              <p className="text-sm text-gray-400 mt-1">
                {course.course_code} - {course.course_title}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Session Date"
              name="session_date"
              type="date"
              value={formData.session_date}
              onChange={handleChange}
              error={errors.session_date}
              required
              icon={Calendar}
            />

            <Select
              label="Duration"
              name="duration_minutes"
              value={formData.duration_minutes}
              onChange={handleChange}
              options={durationOptions}
              required
            />
          </div>

          <Input
            label="Session Topic"
            name="session_topic"
            value={formData.session_topic}
            onChange={handleChange}
            placeholder="e.g., Introduction to React Hooks"
            error={errors.session_topic}
            required
          />

          <Select
            label="Session Type"
            name="session_type"
            value={formData.session_type}
            onChange={handleChange}
            options={sessionTypeOptions}
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Session Notes (Optional)
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows="3"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Any additional notes about this session..."
            />
          </div>

          {/* Information */}
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
            <div className="flex items-start">
              <Camera className="h-5 w-5 text-green-400 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <p className="text-green-400 text-sm font-medium">
                  Attendance Session
                </p>
                <p className="text-green-300 text-sm mt-1">
                  Students will be able to mark their attendance using facial
                  recognition during this session. Make sure students are
                  present and ready to scan their faces.
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
              className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700"
            >
              <Camera className="h-4 w-4 mr-2" />
              Start Session
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateSessionModal;
