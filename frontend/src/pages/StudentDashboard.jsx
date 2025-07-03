import React, { useState, useEffect } from "react";
import {
  BookOpen,
  Camera,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Calendar,
  TrendingUp,
  User,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useAttendance } from "../hooks/useAttendance";
import { useCourses } from "../hooks/useCourses";
import Button from "../components/common/Button";
import Card from "../components/common/Card";
import Modal from "../components/common/Modal";
import FaceRecognitionModal from "../components/student/FaceRecognitionModal";
import AttendanceHistory from "../components/student/AttendanceHistory";

const StudentDashboard = () => {
  const { user } = useAuth();
  const { enrolledCourses, availableSessions } = useCourses();
  const { studentAttendance, markAttendance } = useAttendance();

  const [showFaceRecognition, setShowFaceRecognition] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [attendanceStats, setAttendanceStats] = useState({});

  useEffect(() => {
    if (enrolledCourses.length > 0) {
      loadAttendanceStats();
    }
  }, [enrolledCourses, studentAttendance]);

  const loadAttendanceStats = () => {
    const stats = enrolledCourses.reduce((acc, course) => {
      const courseAttendances = studentAttendance.filter(
        (a) => a.course_id === course.id
      );
      const present = courseAttendances.filter(
        (a) => a.status === "present"
      ).length;
      const late = courseAttendances.filter((a) => a.status === "late").length;
      const total = courseAttendances.length;
      const rate = total > 0 ? ((present + late) / total) * 100 : 0;

      acc[course.id] = {
        present,
        late,
        total,
        rate: Math.round(rate),
      };
      return acc;
    }, {});

    setAttendanceStats(stats);
  };

  const handleMarkAttendance = async (sessionId) => {
    setSelectedSession(sessionId);
    setShowFaceRecognition(true);
  };

  const handleFaceRecognitionSuccess = async (faceData) => {
    try {
      await markAttendance(selectedSession, faceData);
      setShowFaceRecognition(false);
      setSelectedSession(null);
      // Refresh data
      loadAttendanceStats();
    } catch (error) {
      console.error("Error marking attendance:", error);
    }
  };

  const overallStats =
    enrolledCourses.length > 0
      ? {
          totalCourses: enrolledCourses.length,
          averageAttendance: Math.round(
            Object.values(attendanceStats).reduce(
              (sum, stat) => sum + stat.rate,
              0
            ) / Math.max(Object.keys(attendanceStats).length, 1)
          ),
          totalClasses: Object.values(attendanceStats).reduce(
            (sum, stat) => sum + stat.total,
            0
          ),
          presentClasses: Object.values(attendanceStats).reduce(
            (sum, stat) => sum + stat.present + stat.late,
            0
          ),
        }
      : {
          totalCourses: 0,
          averageAttendance: 0,
          totalClasses: 0,
          presentClasses: 0,
        };

  const statsCards = [
    {
      title: "Enrolled Courses",
      value: overallStats.totalCourses,
      icon: BookOpen,
      color: "primary",
      subtitle: "This semester",
    },
    {
      title: "Overall Attendance",
      value: `${overallStats.averageAttendance}%`,
      icon: TrendingUp,
      color:
        overallStats.averageAttendance >= 75
          ? "success"
          : overallStats.averageAttendance >= 60
          ? "warning"
          : "danger",
      subtitle: "Across all courses",
    },
    {
      title: "Classes Attended",
      value: `${overallStats.presentClasses}/${overallStats.totalClasses}`,
      icon: CheckCircle,
      color: "info",
      subtitle: "Total sessions",
    },
    {
      title: "Face Status",
      value: user?.is_face_registered ? "Registered" : "Not Registered",
      icon: User,
      color: user?.is_face_registered ? "success" : "warning",
      subtitle: user?.is_face_registered
        ? "Ready for attendance"
        : "See lecturer to register",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome back, {user?.full_name}
          </h1>
          <p className="text-gray-300">
            {user?.programme} - Level {user?.level}
          </p>
          <p className="text-gray-400 text-sm">
            {user?.student_id || user?.matric_number} • {user?.college}
          </p>
        </div>

        {/* Face Registration Warning */}
        {!user?.is_face_registered && (
          <div className="mb-8">
            <Card className="p-4 border-l-4 border-yellow-500 bg-yellow-500/10">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-400" />
                <div>
                  <p className="text-yellow-400 font-medium">
                    Face Registration Required
                  </p>
                  <p className="text-gray-300 text-sm">
                    Please see your lecturer to register your face before you
                    can mark attendance.
                  </p>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statsCards.map((stat, index) => {
            const IconComponent = stat.icon;
            return (
              <Card key={index} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400 mb-1">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-white mb-1">
                      {stat.value}
                    </p>
                    <p className="text-xs text-gray-500">{stat.subtitle}</p>
                  </div>
                  <div
                    className={`h-12 w-12 bg-${stat.color}-500/20 rounded-lg flex items-center justify-center`}
                  >
                    <IconComponent
                      className={`h-6 w-6 text-${stat.color}-400`}
                    />
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Available Sessions for Attendance */}
        {availableSessions.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">
              Mark Attendance
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableSessions.map((session) => (
                <Card key={session.id} className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 bg-green-400 rounded-full animate-pulse" />
                      <span className="text-white font-medium">
                        {session.course_code}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">Active</span>
                  </div>

                  <p className="text-gray-300 text-sm mb-3">
                    {session.course_title}
                  </p>

                  {session.session_topic && (
                    <p className="text-gray-400 text-xs mb-3">
                      Topic: {session.session_topic}
                    </p>
                  )}

                  <div className="flex items-center justify-between mb-4">
                    <div className="text-xs text-gray-400">
                      <p>{session.classroom}</p>
                      <p>
                        {new Date(session.session_date).toLocaleTimeString()}
                      </p>
                    </div>
                    <div className="text-xs text-gray-400">
                      {session.duration_minutes} min
                    </div>
                  </div>

                  <Button
                    onClick={() => handleMarkAttendance(session.id)}
                    disabled={!user?.is_face_registered}
                    className="w-full flex items-center justify-center gap-2"
                    variant="primary"
                  >
                    <Camera className="h-4 w-4" />
                    Mark Attendance
                  </Button>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Enrolled Courses */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">My Courses</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {enrolledCourses.map((course) => {
              const stats = attendanceStats[course.id] || {
                present: 0,
                late: 0,
                total: 0,
                rate: 0,
              };

              return (
                <Card key={course.id} className="p-6">
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold text-white mb-1">
                      {course.course_code}
                    </h3>
                    <p className="text-gray-300 text-sm mb-2">
                      {course.course_title}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>{course.course_unit} Units</span>
                      <span>{course.semester}</span>
                    </div>
                  </div>

                  {/* Attendance Progress */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-400">
                        Attendance Rate
                      </span>
                      <span
                        className={`text-sm font-medium ${
                          stats.rate >= 75
                            ? "text-green-400"
                            : stats.rate >= 60
                            ? "text-yellow-400"
                            : "text-red-400"
                        }`}
                      >
                        {stats.rate}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          stats.rate >= 75
                            ? "bg-green-400"
                            : stats.rate >= 60
                            ? "bg-yellow-400"
                            : "bg-red-400"
                        }`}
                        style={{ width: `${stats.rate}%` }}
                      />
                    </div>
                  </div>

                  {/* Attendance Stats */}
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="p-2 bg-green-500/20 rounded">
                      <p className="text-green-400 font-medium">
                        {stats.present}
                      </p>
                      <p className="text-gray-400">Present</p>
                    </div>
                    <div className="p-2 bg-yellow-500/20 rounded">
                      <p className="text-yellow-400 font-medium">
                        {stats.late}
                      </p>
                      <p className="text-gray-400">Late</p>
                    </div>
                    <div className="p-2 bg-gray-700 rounded">
                      <p className="text-white font-medium">{stats.total}</p>
                      <p className="text-gray-400">Total</p>
                    </div>
                  </div>

                  {/* Lecturer Info */}
                  <div className="mt-4 pt-4 border-t border-gray-700">
                    <p className="text-xs text-gray-400">Lecturer</p>
                    <p className="text-sm text-gray-300">
                      {course.lecturer_name}
                    </p>
                    {course.class_days && (
                      <p className="text-xs text-gray-400 mt-1">
                        {course.class_days.join(", ")} •{" "}
                        {course.class_time_start}-{course.class_time_end}
                      </p>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Recent Attendance History */}
        <AttendanceHistory attendance={studentAttendance.slice(0, 5)} />
      </div>

      {/* Face Recognition Modal */}
      <FaceRecognitionModal
        isOpen={showFaceRecognition}
        onClose={() => {
          setShowFaceRecognition(false);
          setSelectedSession(null);
        }}
        onSuccess={handleFaceRecognitionSuccess}
        sessionId={selectedSession}
      />
    </div>
  );
};

export default StudentDashboard;
