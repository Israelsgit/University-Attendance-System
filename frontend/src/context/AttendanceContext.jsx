// frontend/src/context/AttendanceContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import { attendanceService } from "../services/attendance";
import { courseService } from "../services/courseService";
import toast from "react-hot-toast";

const AttendanceContext = createContext();

export const useAttendance = () => {
  const context = useContext(AttendanceContext);
  if (!context) {
    throw new Error("useAttendance must be used within an AttendanceProvider");
  }
  return context;
};

// Attendance status constants
export const ATTENDANCE_STATUS = {
  PRESENT: "present",
  ABSENT: "absent",
  LATE: "late",
  EXCUSED: "excused",
  PENDING: "pending",
};

export const AttendanceProvider = ({ children }) => {
  // Student-related state
  const [studentAttendance, setStudentAttendance] = useState([]);
  const [availableSessions, setAvailableSessions] = useState([]);
  const [attendanceStats, setAttendanceStats] = useState(null);

  // Lecturer-related state
  const [activeSessions, setActiveSessions] = useState([]);
  const [courseAnalytics, setCourseAnalytics] = useState({});
  const [sessionAttendees, setSessionAttendees] = useState({});

  // Shared state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Real-time session updates
  const [sessionStatus, setSessionStatus] = useState({});

  // Load initial data based on user role
  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("attendance_user") || "{}");
    if (user.role === "student") {
      loadStudentData();
    } else if (user.role === "lecturer" || user.role === "admin") {
      loadLecturerData();
    }
  }, []);

  // Student functions
  const loadStudentData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadStudentAttendance(),
        loadAvailableSessions(),
        loadAttendanceStats(),
      ]);
    } catch (error) {
      console.error("Failed to load student data:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadStudentAttendance = async (courseId = null) => {
    try {
      const data = await attendanceService.getStudentAttendance(courseId);
      setStudentAttendance(data);
      return data;
    } catch (error) {
      console.error("Failed to load student attendance:", error);
      throw error;
    }
  };

  const loadAvailableSessions = async () => {
    try {
      const data = await courseService.getAvailableSessions();
      setAvailableSessions(data);
      return data;
    } catch (error) {
      console.error("Failed to load available sessions:", error);
      throw error;
    }
  };

  const loadAttendanceStats = async () => {
    try {
      const data = await attendanceService.getStudentAttendance();

      // Calculate stats from attendance data
      const stats = calculateAttendanceStats(data);
      setAttendanceStats(stats);
      return stats;
    } catch (error) {
      console.error("Failed to load attendance stats:", error);
      throw error;
    }
  };

  const markAttendance = async (sessionId, imageBlob) => {
    try {
      setLoading(true);
      const result = await attendanceService.markAttendance(
        sessionId,
        imageBlob
      );

      toast.success("Attendance marked successfully!");

      // Refresh student data
      await loadStudentData();

      return result;
    } catch (error) {
      const errorMessage = error.message || "Failed to mark attendance";
      toast.error(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Lecturer functions
  const loadLecturerData = async () => {
    try {
      setLoading(true);
      await loadActiveSessions();
    } catch (error) {
      console.error("Failed to load lecturer data:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadActiveSessions = async () => {
    try {
      // This would typically come from a lecturer-specific endpoint
      const courses = await courseService.getMyCourses();
      const sessions = [];

      // Extract active sessions from courses
      courses.forEach((course) => {
        if (course.active_sessions) {
          sessions.push(...course.active_sessions);
        }
      });

      setActiveSessions(sessions);
      return sessions;
    } catch (error) {
      console.error("Failed to load active sessions:", error);
      throw error;
    }
  };

  const activateSession = async (sessionId) => {
    try {
      setLoading(true);
      const result = await attendanceService.activateSession(sessionId);

      // Update session status
      setSessionStatus((prev) => ({
        ...prev,
        [sessionId]: { active: true, startTime: new Date() },
      }));

      toast.success("Session activated! Students can now mark attendance.");

      // Refresh active sessions
      await loadActiveSessions();

      return result;
    } catch (error) {
      const errorMessage = error.message || "Failed to activate session";
      toast.error(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deactivateSession = async (sessionId) => {
    try {
      setLoading(true);
      const result = await attendanceService.deactivateSession(sessionId);

      // Update session status
      setSessionStatus((prev) => ({
        ...prev,
        [sessionId]: { active: false, endTime: new Date() },
      }));

      toast.success("Session deactivated!");

      // Refresh active sessions
      await loadActiveSessions();

      return result;
    } catch (error) {
      const errorMessage = error.message || "Failed to deactivate session";
      toast.error(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loadCourseAnalytics = async (courseId) => {
    try {
      setLoading(true);
      const data = await attendanceService.getCourseAnalytics(courseId);

      setCourseAnalytics((prev) => ({
        ...prev,
        [courseId]: data,
      }));

      return data;
    } catch (error) {
      console.error("Failed to load course analytics:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loadSessionAttendees = async (sessionId) => {
    try {
      // This would be a new endpoint to get attendees for a specific session
      const data =
        (await attendanceService.getSessionAttendees?.(sessionId)) || [];

      setSessionAttendees((prev) => ({
        ...prev,
        [sessionId]: data,
      }));

      return data;
    } catch (error) {
      console.error("Failed to load session attendees:", error);
      throw error;
    }
  };

  // Utility functions
  const calculateAttendanceStats = (attendanceData) => {
    if (!attendanceData || attendanceData.length === 0) {
      return {
        totalSessions: 0,
        presentSessions: 0,
        lateSessions: 0,
        absentSessions: 0,
        attendanceRate: 0,
        status: "no-data",
      };
    }

    const totalSessions = attendanceData.length;
    const presentSessions = attendanceData.filter(
      (record) => record.status === ATTENDANCE_STATUS.PRESENT
    ).length;
    const lateSessions = attendanceData.filter(
      (record) => record.status === ATTENDANCE_STATUS.LATE
    ).length;
    const absentSessions = attendanceData.filter(
      (record) => record.status === ATTENDANCE_STATUS.ABSENT
    ).length;

    const attendanceRate = Math.round(
      ((presentSessions + lateSessions) / totalSessions) * 100
    );

    let status = "good";
    if (attendanceRate < 60) {
      status = "poor";
    } else if (attendanceRate < 75) {
      status = "warning";
    }

    return {
      totalSessions,
      presentSessions,
      lateSessions,
      absentSessions,
      attendanceRate,
      status,
    };
  };

  const getAttendanceForCourse = (courseId) => {
    return studentAttendance.filter((record) => record.course_id === courseId);
  };

  const getSessionById = (sessionId) => {
    return (
      availableSessions.find((session) => session.id === sessionId) ||
      activeSessions.find((session) => session.id === sessionId)
    );
  };

  const isSessionActive = (sessionId) => {
    return sessionStatus[sessionId]?.active || false;
  };

  // Refresh all data
  const refreshData = async () => {
    const user = JSON.parse(localStorage.getItem("attendance_user") || "{}");
    if (user.role === "student") {
      await loadStudentData();
    } else if (user.role === "lecturer" || user.role === "admin") {
      await loadLecturerData();
    }
  };

  const value = {
    // Student state
    studentAttendance,
    availableSessions,
    attendanceStats,

    // Lecturer state
    activeSessions,
    courseAnalytics,
    sessionAttendees,
    sessionStatus,

    // Shared state
    loading,
    error,

    // Student actions
    markAttendance,
    loadStudentAttendance,
    loadAvailableSessions,
    loadAttendanceStats,

    // Lecturer actions
    activateSession,
    deactivateSession,
    loadCourseAnalytics,
    loadSessionAttendees,
    loadActiveSessions,

    // Utility functions
    calculateAttendanceStats,
    getAttendanceForCourse,
    getSessionById,
    isSessionActive,

    // General actions
    refreshData,

    // Constants
    ATTENDANCE_STATUS,
  };

  return (
    <AttendanceContext.Provider value={value}>
      {children}
    </AttendanceContext.Provider>
  );
};

export { AttendanceContext };
