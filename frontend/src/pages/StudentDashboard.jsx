import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-hot-toast";
import {
  Calendar,
  Clock,
  BookOpen,
  CheckCircle,
  XCircle,
  Camera,
  User,
  TrendingUp,
  AlertTriangle,
  Eye,
  GraduationCap,
} from "lucide-react";

import { useAuth } from "../hooks/useAuth";
import { attendanceAPI, courseAPI } from "../services/apiClient";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Button from "../components/common/Button";
import AttendanceChart from "../components/charts/AttendanceChart";
import FaceRegistrationModal from "../components/modals/FaceRegisterationModal";

const StudentDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [attendanceData, setAttendanceData] = useState([]);
  const [todayAttendance, setTodayAttendance] = useState(null);
  const [activeSessions, setActiveSessions] = useState([]);
  const [attendanceSummary, setAttendanceSummary] = useState(null);
  const [showFaceRegistration, setShowFaceRegistration] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load all student data in parallel
      const [coursesRes, attendanceRes, todayRes, sessionsRes] =
        await Promise.all([
          courseAPI.getEnrolledCourses(),
          attendanceAPI.getMyAttendance(),
          attendanceAPI.getTodayAttendance(),
          attendanceAPI.getActiveSessions(),
        ]);

      setEnrolledCourses(coursesRes.data.courses || []);
      setAttendanceData(attendanceRes.data.attendance_records || []);
      setAttendanceSummary(attendanceRes.data.summary || null);
      setTodayAttendance(todayRes.data);
      setActiveSessions(sessionsRes.data.sessions || []);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAttendance = async (sessionId) => {
    try {
      if (!user?.is_face_registered) {
        toast.error("Please register your face first to mark attendance");
        setShowFaceRegistration(true);
        return;
      }

      const response = await attendanceAPI.markAttendance(sessionId);
      toast.success(response.data.message);

      // Reload data
      loadDashboardData();
    } catch (error) {
      console.error("Failed to mark attendance:", error);
      toast.error(error.response?.data?.detail || "Failed to mark attendance");
    }
  };

  const handleFaceRegistrationSuccess = () => {
    setShowFaceRegistration(false);
    toast.success("Face registered successfully! You can now mark attendance.");
    loadDashboardData();
  };

  const getAttendanceStatus = (percentage) => {
    if (percentage >= 80)
      return {
        status: "excellent",
        color: "text-green-400",
        bgColor: "bg-green-500/10",
        borderColor: "border-green-500/20",
      };
    if (percentage >= 70)
      return {
        status: "good",
        color: "text-blue-400",
        bgColor: "bg-blue-500/10",
        borderColor: "border-blue-500/20",
      };
    if (percentage >= 60)
      return {
        status: "average",
        color: "text-yellow-400",
        bgColor: "bg-yellow-500/10",
        borderColor: "border-yellow-500/20",
      };
    return {
      status: "poor",
      color: "text-red-400",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/20",
    };
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
                {user?.programme} - Level {user?.level}
              </p>
              <p className="text-sm text-gray-500">
                {user?.matric_number} • {user?.college}
              </p>
            </div>

            {/* Face Registration Status */}
            <div className="text-right">
              {!user?.is_face_registered && (
                <div className="mb-4">
                  <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4">
                    <div className="flex items-center text-amber-400">
                      <AlertTriangle className="h-5 w-5 mr-2" />
                      <span className="text-sm font-medium">
                        Face Registration Required
                      </span>
                    </div>
                    <p className="text-xs text-amber-300 mt-1">
                      Please register your face to mark attendance
                    </p>
                    <Button
                      onClick={() => setShowFaceRegistration(true)}
                      variant="primary"
                      size="small"
                      className="mt-2 bg-amber-600 hover:bg-amber-700"
                    >
                      <Camera className="h-4 w-4 mr-2" />
                      Register Face
                    </Button>
                  </div>
                </div>
              )}

              <div className="text-sm text-gray-400">
                Today:{" "}
                {new Date().toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Today's Attendance */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Today's Sessions</p>
                <p className="text-2xl font-bold text-white">
                  {todayAttendance?.attended_sessions || 0}/
                  {todayAttendance?.today_sessions || 0}
                </p>
              </div>
              <div className="p-3 bg-blue-500/20 rounded-lg">
                <Calendar className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          {/* Overall Attendance */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Overall Attendance</p>
                <p className="text-2xl font-bold text-white">
                  {attendanceSummary?.attendance_percentage?.toFixed(1) || 0}%
                </p>
              </div>
              <div className="p-3 bg-green-500/20 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-400" />
              </div>
            </div>
          </div>

          {/* Enrolled Courses */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Enrolled Courses</p>
                <p className="text-2xl font-bold text-white">
                  {enrolledCourses.length}
                </p>
              </div>
              <div className="p-3 bg-purple-500/20 rounded-lg">
                <BookOpen className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </div>

          {/* Total Sessions */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Sessions</p>
                <p className="text-2xl font-bold text-white">
                  {attendanceSummary?.attended_sessions || 0}/
                  {attendanceSummary?.total_sessions || 0}
                </p>
              </div>
              <div className="p-3 bg-orange-500/20 rounded-lg">
                <Clock className="h-6 w-6 text-orange-400" />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Active Sessions */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">
                Active Sessions
              </h2>
              <Camera className="h-5 w-5 text-gray-400" />
            </div>

            {activeSessions.length > 0 ? (
              <div className="space-y-4">
                {activeSessions.map((session) => (
                  <div
                    key={session.id}
                    className="bg-white/5 rounded-lg p-4 border border-white/10"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-white">
                          {session.course_code}
                        </h3>
                        <p className="text-sm text-gray-400">
                          {session.course_title}
                        </p>
                        <p className="text-xs text-gray-500">
                          {session.start_time} - {session.end_time}
                        </p>
                      </div>
                      <Button
                        onClick={() => handleMarkAttendance(session.id)}
                        variant="primary"
                        size="small"
                        className="bg-green-600 hover:bg-green-700"
                        disabled={!user?.is_face_registered}
                      >
                        <Camera className="h-4 w-4 mr-2" />
                        Mark Attendance
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Clock className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No active sessions right now</p>
                <p className="text-sm text-gray-500">
                  Come back when your lecturer starts a session
                </p>
              </div>
            )}
          </div>

          {/* My Courses */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">My Courses</h2>
              <BookOpen className="h-5 w-5 text-gray-400" />
            </div>

            {enrolledCourses.length > 0 ? (
              <div className="space-y-4">
                {enrolledCourses.map((course) => {
                  const attendanceStatus = getAttendanceStatus(
                    course.attendance_percentage || 0
                  );

                  return (
                    <div
                      key={course.id}
                      className={`rounded-lg p-4 border ${attendanceStatus.bgColor} ${attendanceStatus.borderColor}`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium text-white">
                            {course.course_code}
                          </h3>
                          <p className="text-sm text-gray-400">
                            {course.course_title}
                          </p>
                          <p className="text-xs text-gray-500">
                            {course.lecturer_name}
                          </p>
                        </div>
                        <div className="text-right">
                          <div
                            className={`text-lg font-bold ${attendanceStatus.color}`}
                          >
                            {course.attendance_percentage?.toFixed(1) || 0}%
                          </div>
                          <p className="text-xs text-gray-500">
                            {course.attended_sessions || 0}/
                            {course.total_sessions || 0} sessions
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <BookOpen className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No enrolled courses</p>
                <p className="text-sm text-gray-500">
                  Contact your lecturer to be enrolled in courses
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Attendance */}
        <div className="mt-8 bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">
              Recent Attendance
            </h2>
            <Link
              to="/my-attendance"
              className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
            >
              View All
            </Link>
          </div>

          {attendanceData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left text-gray-400 text-sm font-medium pb-3">
                      Course
                    </th>
                    <th className="text-left text-gray-400 text-sm font-medium pb-3">
                      Date
                    </th>
                    <th className="text-left text-gray-400 text-sm font-medium pb-3">
                      Status
                    </th>
                    <th className="text-left text-gray-400 text-sm font-medium pb-3">
                      Time
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {attendanceData.slice(0, 5).map((record) => (
                    <tr key={record.id} className="border-b border-white/5">
                      <td className="py-3">
                        <div>
                          <p className="text-white font-medium">
                            {record.course_code}
                          </p>
                          <p className="text-sm text-gray-400">
                            {record.course_title}
                          </p>
                        </div>
                      </td>
                      <td className="py-3 text-gray-300">
                        {new Date(record.session_date).toLocaleDateString()}
                      </td>
                      <td className="py-3">
                        <div className="flex items-center">
                          {record.status === "present" ? (
                            <>
                              <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                              <span className="text-green-400">Present</span>
                            </>
                          ) : (
                            <>
                              <XCircle className="h-4 w-4 text-red-400 mr-2" />
                              <span className="text-red-400">Absent</span>
                            </>
                          )}
                        </div>
                      </td>
                      <td className="py-3 text-gray-400">
                        {record.marked_at
                          ? new Date(record.marked_at).toLocaleTimeString()
                          : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <Eye className="h-12 w-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No attendance records yet</p>
              <p className="text-sm text-gray-500">
                Your attendance will appear here after you mark attendance
              </p>
            </div>
          )}
        </div>

        {/* Attendance Chart */}
        {attendanceData.length > 0 && (
          <div className="mt-8 bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <h2 className="text-xl font-semibold text-white mb-6">
              Attendance Trend
            </h2>
            <AttendanceChart data={attendanceData} />
          </div>
        )}
      </div>

      {/* Face Registration Modal */}
      {showFaceRegistration && (
        <FaceRegistrationModal
          isOpen={showFaceRegistration}
          onClose={() => setShowFaceRegistration(false)}
          onSuccess={handleFaceRegistrationSuccess}
        />
      )}
    </div>
  );
};

export default StudentDashboard;
