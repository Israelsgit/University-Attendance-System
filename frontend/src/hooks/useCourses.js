import { useState, useEffect } from "react";
import { courseService } from "../services/courseService";
import toast from "react-hot-toast";

export const useCourses = () => {
  const [courses, setCourses] = useState([]);
  const [activeSessions, setActiveSessions] = useState([]);
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [availableSessions, setAvailableSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const data = await courseService.getMyCourses();
      setCourses(data);

      const user = JSON.parse(localStorage.getItem("attendance_user") || "{}");
      if (user.role === "student") {
        setEnrolledCourses(data);
      }
    } catch (error) {
      setError(error.message);
      toast.error("Failed to fetch courses");
    } finally {
      setLoading(false);
    }
  };

  const createCourse = async (courseData) => {
    try {
      await courseService.createCourse(courseData);
      toast.success("Course created successfully!");
      fetchCourses();
    } catch (error) {
      toast.error(error.message || "Failed to create course");
      throw error;
    }
  };

  const enrollStudent = async (courseId, studentEmail) => {
    try {
      await courseService.enrollStudent(courseId, studentEmail);
      toast.success("Student enrolled successfully!");
      fetchCourses();
    } catch (error) {
      toast.error(error.message || "Failed to enroll student");
      throw error;
    }
  };

  const createSession = async (courseId, sessionData) => {
    try {
      const result = await courseService.createSession(courseId, sessionData);
      toast.success("Class session created!");
      return result;
    } catch (error) {
      toast.error(error.message || "Failed to create session");
      throw error;
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  return {
    courses,
    activeSessions,
    enrolledCourses,
    availableSessions,
    loading,
    error,
    createCourse,
    enrollStudent,
    createSession,
    refetch: fetchCourses,
  };
};
