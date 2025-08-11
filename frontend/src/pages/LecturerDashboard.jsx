import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-hot-toast";
import {
  Plus,
  Users,
  BookOpen,
  BarChart3,
  Calendar,
  Clock,
  TrendingUp,
  Settings,
  UserPlus,
  Camera,
  Download,
  Eye,
  Edit,
  Trash2,
  Shield,
} from "lucide-react";

import { useAuth } from "../hooks/useAuth";
import { courseAPI, analyticsAPI, attendanceAPI } from "../services/apiClient";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Button from "../components/common/Button";
import CreateCourseModal from "../components/modals/CreateCourseModal";
import EnrollStudentModal from "../components/modals/EnrollStudentModal";
import CreateSessionModal from "../components/modals/CreateSessionModal";
import DashboardChart from "../components/charts/DashboardChart";

const LecturerDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardStats, setDashboardStats] = useState({});
  const [myCourses, setMyCourses] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [attendanceTrends, setAttendanceTrends] = useState([]);

  // Modal states
  const [showCreateCourse, setShowCreateCourse] = useState(false);
  const [showEnrollStudent, setShowEnrollStudent] = useState(false);
  const [showCreateSession, setShowCreateSession] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load lecturer dashboard data
      const [statsRes, coursesRes, trendsRes] = await Promise.all([
        analyticsAPI.getDashboardStats(),
        courseAPI.getMyCourses(),
        analyticsAPI.getAttendanceTrends("month"),
      ]);

      setDashboardStats(statsRes.data);
      setMyCourses(coursesRes.data.courses || []);
      setAttendanceTrends(trendsRes.data.trends || []);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = async (courseData) => {
    try {
      await courseAPI.createCourse(courseData);
      toast.success("Course created successfully!");
      setShowCreateCourse(false);
      loadDashboardData();
    } catch (error) {
      console.error("Failed to create course:", error);
      toast.error(error.response?.data?.detail || "Failed to create course");
    }
  };

  const handleEnrollStudent = async (enrollmentData) => {
    try {
      await courseAPI.enrollStudent(
        selectedCourse.id,
        enrollmentData.student_email
      );
      toast.success("Student enrolled successfully!");
      setShowEnrollStudent(false);
      setSelectedCourse(null);
      loadDashboardData();
    } catch (error) {
      console.error("Failed to enroll student:", error);
      toast.error(error.response?.data?.detail || "Failed to enroll student");
    }
  };

  const handleCreateSession = async (sessionData) => {
    try {
      await attendanceAPI.createSession(selectedCourse.id, sessionData);
      toast.success("Attendance session created successfully!");
      setShowCreateSession(false);
      setSelectedCourse(null);
      loadDashboardData();
    } catch (error) {
      console.error("Failed to create session:", error);
      toast.error(error.response?.data?.detail || "Failed to create session");
    }
  };

  const handleDeleteCourse = async (courseId) => {
    if (!window.confirm("Are you sure you want to delete this course?")) {
      return;
    }

    try {
      await courseAPI.deleteCourse(courseId);
      toast.success("Course deleted successfully!");
      loadDashboardData();
    } catch (error) {
      console.error("Failed to delete course:", error);
      toast.error(error.response?.data?.detail || "Failed to delete course");
    }
  };

  const handleExportAttendance = async (courseId) => {
    try {
      const response = await analyticsAPI.exportAttendanceData(courseId, "csv");

      // Create download link
      const blob = new Blob([response.data], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `attendance_${courseId}_${new Date().toISOString().split("T")[0]}.csv`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success("Attendance data exported successfully!");
    } catch (error) {
      console.error("Failed to export attendance:", error);
      toast.error("Failed to export attendance data");
    }
  };

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
                Welcome back, {user?.full_name}
              </h1>
              <p className="text-gray-400">
                {user?.department} - {user?.college}
              </p>
              <p className="text-sm text-gray-500 flex items-center">
                <Shield className="h-4 w-4 mr-1" />
                {user?.staff_id} • Administrative Access
              </p>
            </div>

            {/* Quick Actions */}
            <div className="flex gap-3">
              <Button
                onClick={() => setShowCreateCourse(true)}
                variant="primary"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Course
              </Button>

              <Button
                onClick={() => setShowEnrollStudent(true)}
                variant="secondary"
                disabled={myCourses.length === 0}
              >
                <UserPlus className="h-4 w-4 mr-2" />
                Enroll Student
              </Button>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Courses */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Courses</p>
                <p className="text-2xl font-bold text-white">
                  {dashboardStats.total_courses || 0}
                </p>
                <p className="text-xs text-gray-500">Active this semester</p>
              </div>
              <div className="p-3 bg-blue-500/20 rounded-lg">
                <BookOpen className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          {/* Total Students */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Students</p>
                <p className="text-2xl font-bold text-white">
                  {dashboardStats.total_students || 0}
                </p>
                <p className="text-xs text-gray-500">Across all courses</p>
              </div>
              <div className="p-3 bg-green-500/20 rounded-lg">
                <Users className="h-6 w-6 text-green-400" />
              </div>
            </div>
          </div>

          {/* Active Sessions */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Sessions</p>
                <p className="text-2xl font-bold text-white">
                  {dashboardStats.active_sessions || 0}
                </p>
                <p className="text-xs text-gray-500">
                  Currently taking attendance
                </p>
              </div>
              <div className="p-3 bg-orange-500/20 rounded-lg">
                <Clock className="h-6 w-6 text-orange-400" />
              </div>
            </div>
          </div>

          {/* Average Attendance */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Avg Attendance</p>
                <p className="text-2xl font-bold text-white">
                  {dashboardStats.average_attendance?.toFixed(1) || 0}%
                </p>
                <p className="text-xs text-gray-500">Overall performance</p>
              </div>
              <div className="p-3 bg-purple-500/20 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* My Courses */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">My Courses</h2>
              <div className="flex gap-2">
                <Link
                  to="/analytics"
                  className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
                >
                  View Analytics
                </Link>
              </div>
            </div>

            {myCourses.length > 0 ? (
              <div className="space-y-4">
                {myCourses.map((course) => (
                  <div
                    key={course.id}
                    className="bg-white/5 rounded-lg p-4 border border-white/10"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-white">
                            {course.course_code}
                          </h3>
                          <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                            {course.course_units} units
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 mb-2">
                          {course.course_title}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>{course.students_count || 0} students</span>
                          <span>{course.sessions_count || 0} sessions</span>
                          <span>{course.level} Level</span>
                        </div>
                      </div>

                      <div className="flex flex-col gap-2">
                        <div className="flex gap-1">
                          <Button
                            onClick={() => {
                              setSelectedCourse(course);
                              setShowEnrollStudent(true);
                            }}
                            variant="secondary"
                            size="small"
                          >
                            <UserPlus className="h-3 w-3" />
                          </Button>

                          <Button
                            onClick={() => {
                              setSelectedCourse(course);
                              setShowCreateSession(true);
                            }}
                            variant="secondary"
                            size="small"
                          >
                            <Camera className="h-3 w-3" />
                          </Button>

                          <Button
                            onClick={() => handleExportAttendance(course.id)}
                            variant="secondary"
                            size="small"
                          >
                            <Download className="h-3 w-3" />
                          </Button>
                        </div>

                        <div className="flex gap-1">
                          <Button
                            onClick={() => {
                              /* Handle edit course */
                            }}
                            variant="secondary"
                            size="small"
                          >
                            <Edit className="h-3 w-3" />
                          </Button>

                          <Button
                            onClick={() => handleDeleteCourse(course.id)}
                            variant="danger"
                            size="small"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BookOpen className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-2">No courses created yet</p>
                <p className="text-sm text-gray-500 mb-4">
                  Create your first course to start managing attendance
                </p>
                <Button
                  onClick={() => setShowCreateCourse(true)}
                  variant="primary"
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Course
                </Button>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <h2 className="text-xl font-semibold text-white mb-6">
              Quick Actions
            </h2>

            <div className="grid grid-cols-1 gap-4">
              {/* Course Management */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex items-center mb-3">
                  <BookOpen className="h-5 w-5 text-blue-400 mr-2" />
                  <h3 className="font-medium text-white">Course Management</h3>
                </div>
                <p className="text-sm text-gray-400 mb-3">
                  Create and manage your courses
                </p>
                <div className="flex gap-2">
                  <Button
                    onClick={() => setShowCreateCourse(true)}
                    variant="primary"
                    size="small"
                  >
                    Create Course
                  </Button>
                  <Link to="/courses">
                    <Button variant="secondary" size="small">
                      <Eye className="h-3 w-3 mr-1" />
                      View All
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Student Management */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex items-center mb-3">
                  <Users className="h-5 w-5 text-green-400 mr-2" />
                  <h3 className="font-medium text-white">Student Management</h3>
                </div>
                <p className="text-sm text-gray-400 mb-3">
                  Enroll students and manage registrations
                </p>
                <div className="flex gap-2">
                  <Button
                    onClick={() => setShowEnrollStudent(true)}
                    variant="primary"
                    size="small"
                    disabled={myCourses.length === 0}
                  >
                    Enroll Student
                  </Button>
                  <Link to="/students">
                    <Button variant="secondary" size="small">
                      <Eye className="h-3 w-3 mr-1" />
                      View All
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Attendance Sessions */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex items-center mb-3">
                  <Camera className="h-5 w-5 text-purple-400 mr-2" />
                  <h3 className="font-medium text-white">
                    Attendance Sessions
                  </h3>
                </div>
                <p className="text-sm text-gray-400 mb-3">
                  Start attendance sessions for your classes
                </p>
                <div className="flex gap-2">
                  <Button
                    onClick={() => setShowCreateSession(true)}
                    variant="primary"
                    size="small"
                    disabled={myCourses.length === 0}
                  >
                    Start Session
                  </Button>
                  <Link to="/attendance">
                    <Button variant="secondary" size="small">
                      <Eye className="h-3 w-3 mr-1" />
                      Manage
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Analytics & Reports */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex items-center mb-3">
                  <BarChart3 className="h-5 w-5 text-orange-400 mr-2" />
                  <h3 className="font-medium text-white">
                    Analytics & Reports
                  </h3>
                </div>
                <p className="text-sm text-gray-400 mb-3">
                  View detailed attendance analytics
                </p>
                <div className="flex gap-2">
                  <Link to="/analytics">
                    <Button variant="primary" size="small">
                      View Analytics
                    </Button>
                  </Link>
                  <Button
                    onClick={() => {
                      if (myCourses.length > 0) {
                        handleExportAttendance(myCourses[0].id);
                      }
                    }}
                    variant="secondary"
                    size="small"
                    disabled={myCourses.length === 0}
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Export
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Attendance Trends Chart */}
        {attendanceTrends.length > 0 && (
          <div className="mt-8 bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">
                Attendance Trends
              </h2>
              <Link
                to="/analytics"
                className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
              >
                View Detailed Analytics
              </Link>
            </div>
            <DashboardChart data={attendanceTrends} />
          </div>
        )}

        {/* System Administration */}
        <div className="mt-8 bg-gradient-to-r from-purple-500/10 to-blue-500/10 backdrop-blur-lg rounded-xl border border-purple-500/20 p-6">
          <div className="flex items-center mb-4">
            <Shield className="h-6 w-6 text-purple-400 mr-3" />
            <h2 className="text-xl font-semibold text-white">
              System Administration
            </h2>
          </div>

          <p className="text-gray-300 mb-4">
            As a lecturer, you have full administrative access to manage the
            attendance system.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/5 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">Course Management</h3>
              <p className="text-sm text-gray-400">
                Create, edit, and delete courses. Set up class schedules and
                requirements.
              </p>
            </div>

            <div className="bg-white/5 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">
                Student Enrollment
              </h3>
              <p className="text-sm text-gray-400">
                Enroll students in courses and manage their face registrations.
              </p>
            </div>

            <div className="bg-white/5 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">System Analytics</h3>
              <p className="text-sm text-gray-400">
                View comprehensive reports and export attendance data.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showCreateCourse && (
        <CreateCourseModal
          isOpen={showCreateCourse}
          onClose={() => setShowCreateCourse(false)}
          onSubmit={handleCreateCourse}
        />
      )}

      {showEnrollStudent && (
        <EnrollStudentModal
          isOpen={showEnrollStudent}
          onClose={() => {
            setShowEnrollStudent(false);
            setSelectedCourse(null);
          }}
          onSubmit={handleEnrollStudent}
          courses={myCourses}
          selectedCourse={selectedCourse}
        />
      )}

      {showCreateSession && (
        <CreateSessionModal
          isOpen={showCreateSession}
          onClose={() => {
            setShowCreateSession(false);
            setSelectedCourse(null);
          }}
          onSubmit={handleCreateSession}
          course={selectedCourse}
        />
      )}
    </div>
  );
};

export default LecturerDashboard;
