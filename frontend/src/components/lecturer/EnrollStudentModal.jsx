import React, { useState } from "react";
import { UserPlus, Search, X } from "lucide-react";
import Button from "../common/Button";
import Input from "../common/Input";
import Select from "../common/Select";
import Modal from "../common/Modal";
import { useCourses } from "../../hooks/useCourses";

const EnrollStudentModal = ({ isOpen, onClose, courses }) => {
  const { enrollStudent } = useCourses();
  const [formData, setFormData] = useState({
    student_email: "",
    course_id: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.student_email || !formData.course_id) {
      setError("Please fill in all fields");
      return;
    }

    setIsLoading(true);
    try {
      await enrollStudent(formData.course_id, formData.student_email);
      onClose();
      setFormData({ student_email: "", course_id: "" });
    } catch (error) {
      setError(error.message || "Failed to enroll student");
    } finally {
      setIsLoading(false);
    }
  };

  const courseOptions = courses.map((course) => ({
    value: course.id,
    label: `${course.course_code} - ${course.course_title}`,
  }));

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Enroll Student in Course">
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div className="space-y-4">
          <Input
            label="Student Email"
            name="student_email"
            type="email"
            value={formData.student_email}
            onChange={handleChange}
            placeholder="student@student.bowen.edu.ng"
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
            required
          />
        </div>

        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <p className="text-blue-400 text-sm">
            <strong>Note:</strong> Make sure the student email is correct. The
            student will be notified of their enrollment and can then register
            their face for attendance.
          </p>
        </div>

        <div className="flex justify-end gap-3">
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
                Enrolling...
              </>
            ) : (
              <>
                <UserPlus className="h-4 w-4" />
                Enroll Student
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default EnrollStudentModal;
