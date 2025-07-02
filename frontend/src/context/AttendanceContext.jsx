import React, { createContext, useContext, useState, useEffect } from "react";
import { attendanceService } from "../services/attendance";
import toast from "react-hot-toast";

const AttendanceContext = createContext();

export const useAttendance = () => {
  const context = useContext(AttendanceContext);
  if (!context) {
    throw new Error("useAttendance must be used within an AttendanceProvider");
  }
  return context;
};

export const AttendanceProvider = ({ children }) => {
  const [todayAttendance, setTodayAttendance] = useState(null);
  const [weeklyStats, setWeeklyStats] = useState(null);
  const [monthlyStats, setMonthlyStats] = useState(null);
  const [attendanceHistory, setAttendanceHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load initial data
  useEffect(() => {
    loadTodayAttendance();
    loadWeeklyStats();
    loadMonthlyStats();
  }, []);

  const loadTodayAttendance = async () => {
    try {
      const data = await attendanceService.getTodayAttendance();
      setTodayAttendance(data);
    } catch (error) {
      console.error("Failed to load today's attendance:", error);
    }
  };

  const loadWeeklyStats = async () => {
    try {
      const data = await attendanceService.getWeeklyStats();
      setWeeklyStats(data);
    } catch (error) {
      console.error("Failed to load weekly stats:", error);
    }
  };

  const loadMonthlyStats = async () => {
    try {
      const data = await attendanceService.getMonthlyStats();
      setMonthlyStats(data);
    } catch (error) {
      console.error("Failed to load monthly stats:", error);
    }
  };

  const loadAttendanceHistory = async (filters = {}) => {
    try {
      setIsLoading(true);
      const data = await attendanceService.getAttendanceHistory(filters);
      setAttendanceHistory(data);
    } catch (error) {
      console.error("Failed to load attendance history:", error);
      toast.error("Failed to load attendance history");
    } finally {
      setIsLoading(false);
    }
  };

  const checkIn = async (faceData) => {
    try {
      setIsLoading(true);
      const result = await attendanceService.checkIn(faceData);

      if (result.success) {
        setTodayAttendance((prev) => ({
          ...prev,
          checkIn: result.timestamp,
          location: result.location,
        }));

        toast.success(
          `Checked in successfully at ${new Date(
            result.timestamp
          ).toLocaleTimeString()}`
        );

        // Refresh stats
        loadWeeklyStats();
        loadMonthlyStats();

        return result;
      } else {
        throw new Error(result.message || "Check-in failed");
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || error.message || "Check-in failed";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const checkOut = async (faceData) => {
    try {
      setIsLoading(true);
      const result = await attendanceService.checkOut(faceData);

      if (result.success) {
        setTodayAttendance((prev) => ({
          ...prev,
          checkOut: result.timestamp,
          totalHours: result.totalHours,
        }));

        toast.success(
          `Checked out successfully at ${new Date(
            result.timestamp
          ).toLocaleTimeString()}`
        );

        // Refresh stats
        loadWeeklyStats();
        loadMonthlyStats();

        return result;
      } else {
        throw new Error(result.message || "Check-out failed");
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || error.message || "Check-out failed";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const manualCheckIn = async (reason) => {
    try {
      setIsLoading(true);
      const result = await attendanceService.manualCheckIn(reason);

      if (result.success) {
        setTodayAttendance((prev) => ({
          ...prev,
          checkIn: result.timestamp,
          isManual: true,
          reason,
        }));

        toast.success("Manual check-in recorded successfully");
        loadWeeklyStats();
        loadMonthlyStats();

        return result;
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Manual check-in failed";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const manualCheckOut = async (reason) => {
    try {
      setIsLoading(true);
      const result = await attendanceService.manualCheckOut(reason);

      if (result.success) {
        setTodayAttendance((prev) => ({
          ...prev,
          checkOut: result.timestamp,
          isManual: true,
          reason,
          totalHours: result.totalHours,
        }));

        toast.success("Manual check-out recorded successfully");
        loadWeeklyStats();
        loadMonthlyStats();

        return result;
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Manual check-out failed";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const requestLeave = async (leaveData) => {
    try {
      setIsLoading(true);
      const result = await attendanceService.requestLeave(leaveData);

      if (result.success) {
        toast.success("Leave request submitted successfully");
        return result;
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Leave request failed";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateAttendance = async (attendanceId, updates) => {
    try {
      setIsLoading(true);
      const result = await attendanceService.updateAttendance(
        attendanceId,
        updates
      );

      if (result.success) {
        toast.success("Attendance updated successfully");

        // Refresh data
        loadTodayAttendance();
        loadWeeklyStats();
        loadMonthlyStats();

        return result;
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || error.message || "Update failed";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    // State
    todayAttendance,
    weeklyStats,
    monthlyStats,
    attendanceHistory,
    isLoading,

    // Actions
    checkIn,
    checkOut,
    manualCheckIn,
    manualCheckOut,
    requestLeave,
    updateAttendance,
    loadAttendanceHistory,
    loadTodayAttendance,
    loadWeeklyStats,
    loadMonthlyStats,
  };

  return (
    <AttendanceContext.Provider value={value}>
      {children}
    </AttendanceContext.Provider>
  );
};

export { AttendanceContext };
