import { useState, useEffect } from "react";
import { attendanceService } from "../services/attendance";
import toast from "react-hot-toast";

export const useAttendance = () => {
  const [studentAttendance, setStudentAttendance] = useState([]);
  const [courseAnalytics, setCourseAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Mark attendance for a session
  const markAttendance = async (sessionId, imageData) => {
    try {
      setLoading(true);
      const result = await attendanceService.markAttendance(
        sessionId,
        imageData
      );

      toast.success(
        `Attendance marked successfully! Status: ${result.status}`,
        { duration: 5000 }
      );

      // Refresh student attendance data
      fetchStudentAttendance();

      return result;
    } catch (error) {
      toast.error(error.message || "Failed to mark attendance");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Get student's attendance history
  const fetchStudentAttendance = async (courseId = null) => {
    try {
      const data = await attendanceService.getStudentAttendance(courseId);
      setStudentAttendance(data.attendance_records || []);
      return data;
    } catch (error) {
      console.error("Failed to fetch student attendance:", error);
      setError(error.message);
    }
  };

  // Get course analytics
  const getCourseAnalytics = async (courseId) => {
    try {
      const data = await attendanceService.getCourseAnalytics(courseId);
      setCourseAnalytics((prev) => ({
        ...prev,
        [courseId]: data,
      }));
      return data;
    } catch (error) {
      console.error("Failed to fetch course analytics:", error);
      throw error;
    }
  };

  // Activate attendance session
  const activateSession = async (sessionId) => {
    try {
      await attendanceService.activateSession(sessionId);
      toast.success("Attendance session activated!");
    } catch (error) {
      toast.error(error.message || "Failed to activate session");
      throw error;
    }
  };

  // Deactivate attendance session
  const deactivateSession = async (sessionId) => {
    try {
      await attendanceService.deactivateSession(sessionId);
      toast.success("Attendance session completed!");
    } catch (error) {
      toast.error(error.message || "Failed to deactivate session");
      throw error;
    }
  };

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("attendance_user") || "{}");
    if (user.role === "student") {
      fetchStudentAttendance();
    }
  }, []);

  return {
    studentAttendance,
    courseAnalytics,
    loading,
    error,
    markAttendance,
    getCourseAnalytics,
    activateSession,
    deactivateSession,
    refetchStudentAttendance: fetchStudentAttendance,
  };
};
