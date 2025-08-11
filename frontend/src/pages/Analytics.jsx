import React, { useState, useEffect } from "react";
import {
  BarChart3,
  TrendingUp,
  Users,
  Calendar,
  Download,
  Filter,
} from "lucide-react";
import { toast } from "react-hot-toast";

import { useAuth } from "../hooks/useAuth";
import { analyticsAPI } from "../services/apiClient";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Button from "../components/common/Button";
import Select from "../components/common/Select";
import DashboardChart from "../components/charts/DashboardChart";
import AttendanceChart from "../components/charts/AttendanceChart";

const Analytics = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState({});
  const [attendanceTrends, setAttendanceTrends] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState("month");
  const [selectedCourse, setSelectedCourse] = useState("");
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    if (user?.role === "lecturer") {
      loadAnalyticsData();
    }
  }, [user, selectedPeriod, selectedCourse]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);

      const [dashboardRes, trendsRes] = await Promise.all([
        analyticsAPI.getDashboardStats(),
        analyticsAPI.getAttendanceTrends(selectedPeriod, selectedCourse),
      ]);

      setAnalyticsData(dashboardRes.data);
      setAttendanceTrends(trendsRes.data.trends || []);
    } catch (error) {
      console.error("Failed to load analytics data:", error);
      toast.error("Failed to load analytics data");
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async () => {
    try {
      if (!selectedCourse) {
        toast.error("Please select a course to export");
        return;
      }

      await analyticsAPI.exportAttendanceData(selectedCourse, "csv");
      toast.success("Data exported successfully!");
    } catch (error) {
      console.error("Export failed:", error);
      toast.error("Failed to export data");
    }
  };

  if (user?.role !== "lecturer") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">
            Access Restricted
          </h2>
          <p className="text-gray-400">Only lecturers can access analytics.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Analytics Dashboard
              </h1>
              <p className="text-gray-400">
                Comprehensive attendance analytics and insights
              </p>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={handleExportData}
                variant="secondary"
                disabled={!selectedCourse}
              >
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-8 bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
          <div className="flex items-center gap-4">
            <Filter className="h-5 w-5 text-gray-400" />
            <div className="flex gap-4 flex-1">
              <Select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                options={[
                  { value: "week", label: "This Week" },
                  { value: "month", label: "This Month" },
                  { value: "semester", label: "This Semester" },
                ]}
                className="w-40"
              />

              <Select
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
                options={[
                  { value: "", label: "All Courses" },
                  ...courses.map((course) => ({
                    value: course.id,
                    label: `${course.course_code} - ${course.course_title}`,
                  })),
                ]}
                className="w-60"
              />
            </div>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Courses</p>
                <p className="text-2xl font-bold text-white">
                  {analyticsData.total_courses || 0}
                </p>
              </div>
              <div className="p-3 bg-blue-500/20 rounded-lg">
                <BarChart3 className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Students</p>
                <p className="text-2xl font-bold text-white">
                  {analyticsData.total_students || 0}
                </p>
              </div>
              <div className="p-3 bg-green-500/20 rounded-lg">
                <Users className="h-6 w-6 text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Sessions</p>
                <p className="text-2xl font-bold text-white">
                  {analyticsData.active_sessions || 0}
                </p>
              </div>
              <div className="p-3 bg-orange-500/20 rounded-lg">
                <Calendar className="h-6 w-6 text-orange-400" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Avg Attendance</p>
                <p className="text-2xl font-bold text-white">
                  {analyticsData.average_attendance?.toFixed(1) || 0}%
                </p>
              </div>
              <div className="p-3 bg-purple-500/20 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Attendance Trends */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <h2 className="text-xl font-semibold text-white mb-6">
              Attendance Trends
            </h2>
            <DashboardChart data={attendanceTrends} type="line" />
          </div>

          {/* Course Performance */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <h2 className="text-xl font-semibold text-white mb-6">
              Course Performance
            </h2>
            <AttendanceChart data={[]} type="bar" />
          </div>
        </div>

        {/* Detailed Analysis */}
        <div className="mt-8 bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
          <h2 className="text-xl font-semibold text-white mb-6">
            Detailed Analysis
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white/5 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">
                Best Performing Course
              </h3>
              <p className="text-2xl font-bold text-green-400">92.5%</p>
              <p className="text-sm text-gray-400">CSC 438 - Web Programming</p>
            </div>

            <div className="bg-white/5 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">Lowest Attendance</h3>
              <p className="text-2xl font-bold text-red-400">67.3%</p>
              <p className="text-sm text-gray-400">
                CSC 412 - Database Systems
              </p>
            </div>

            <div className="bg-white/5 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">
                Average Session Duration
              </h3>
              <p className="text-2xl font-bold text-blue-400">78 min</p>
              <p className="text-sm text-gray-400">Across all courses</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
