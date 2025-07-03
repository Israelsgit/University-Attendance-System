import React, { createContext, useContext, useState, useEffect } from "react";
import { courseService } from "../services/courseService";
import toast from "react-hot-toast";

const CourseContext = createContext();

export const useCourseContext = () => {
  const context = useContext(CourseContext);
  if (!context) {
    throw new Error("useCourseContext must be used within a CourseProvider");
  }
  return context;
};

export const CourseProvider = ({ children }) => {
  const [courses, setCourses] = useState([]);
  const [activeSessions, setActiveSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const data = await courseService.getMyCourses();
      setCourses(data);
    } catch (error) {
      toast.error("Failed to fetch courses");
    } finally {
      setLoading(false);
    }
  };

  const createCourse = async (courseData) => {
    try {
      await courseService.createCourse(courseData);
      toast.success("Course created successfully!");
      await fetchCourses();
    } catch (error) {
      toast.error(error.message || "Failed to create course");
      throw error;
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const value = {
    courses,
    activeSessions,
    loading,
    createCourse,
    fetchCourses,
  };

  return (
    <CourseContext.Provider value={value}>{children}</CourseContext.Provider>
  );
};
