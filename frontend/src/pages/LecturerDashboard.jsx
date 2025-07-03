import React, { useState, useEffect } from "react";
import {
  BookOpen,
  Users,
  Calendar,
  BarChart3,
  Plus,
  Settings,
  UserPlus,
  Camera,
  Clock,
  TrendingUp,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useCourses } from "../hooks/useCourses";
import { useAttendance } from "../hooks/useAttendance";
import Button from "../components/common/Button";
import Card from "../components/common/Card";
import Modal from "../components/common/Modal";
import CreateCourseModal from "../components/lecturer/CreateCourseModal";
import EnrollStudentModal from "../components/lecturer/EnrollStudentModal";
import AttendanceAnalytics from "../components/analytics/AttendanceAnalytics";

const LecturerDashboard = () => {
  const { user } = useAuth();
  const { courses, activeSessions, createSession, updateSession } =
    useCourses();
  const { getCourseAnalytics } = useAttendance();

  const [showCreateCourse, setShowCreateCourse] = useState(false);
  const [showEnrollStudent, setShowEnrollStudent] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [activeSessionsData, setActiveSessionsData] = useState([]);

  useEffect(() => {
    if (courses.length > 0) {
      loadActiveSessions();
    }
  }, [courses]);

  const loadActiveSessions = async () => {
    const sessions = await Promise.all(
      courses.map(async (course) => {
        const analytics = await getCourseAnalytics(course.id);
        return {
          ...course,
          analytics: analytics.summary,
        };
      })
    );
    setActiveSessionsData(sessions);
  };

  const handleStartAttendance = async (courseId) => {
    try {
      const session = await createSession(courseId, {
        session_date: new Date().toISOString(),
        session_topic: "Class Session",
        session_type: "lecture",
        duration_minutes: 60,
      });

      // Activate the session for attendance
      await updateSession(session.session_id, { is_active: true });

      // Refresh data
      loadActiveSessions();
    } catch (error) {
      console.error("Error starting attendance:", error);
    }
  };

  const handleStopAttendance = async (sessionId) => {
    try {
      await updateSession(sessionId, { is_active: false, is_completed: true });
      loadActiveSessions();
    } catch (error) {
      console.error("Error stopping attendance:", error);
    }
  };

  const statsCards = [
    {
      title: "Total Courses",
      value: courses.length,
      icon: BookOpen,
      color: "primary",
      subtitle: "Active courses this semester",
    },
    {
      title: "Total Students",
      value: activeSessionsData.reduce(
        (sum, course) => sum + (course.analytics?.total_students || 0),
        0
      ),
      icon: Users,
      color: "success",
      subtitle: "Across all courses",
    },
    {
      title: "Active Sessions",
      value: activeSessions.length,
      icon: Clock,
      color: "warning",
      subtitle: "Currently taking attendance",
    },
    {
      title: "Avg Attendance",
      value: `${Math.round(
        activeSessionsData.reduce(
          (sum, course) =>
            sum + (course.analytics?.overall_attendance_rate || 0),
          0
        ) / Math.max(activeSessionsData.length, 1)
      )}%`,
      icon: TrendingUp,
      color: "info",
      subtitle: "Overall performance",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome back, Dr. {user?.full_name}
          </h1>
          <p className="text-gray-300">
            {user?.college} - {user?.department}
          </p>
          <p className="text-gray-400 text-sm">Staff ID: {user?.staff_id}</p>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-4">
            <Button
              onClick={() => setShowCreateCourse(true)}
              className="flex items-center gap-2"
              variant="primary"
            >
              <Plus className="h-4 w-4" />
              Create Course
            </Button>
            <Button
              onClick={() => setShowEnrollStudent(true)}
              className="flex items-center gap-2"
              variant="secondary"
            >
              <UserPlus className="h-4 w-4" />
              Enroll Student
            </Button>
          </div>
        </div>

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

        {/* Courses Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          {courses.map((course) => {
            const courseAnalytics = activeSessionsData.find(
              (c) => c.id === course.id
            )?.analytics;
            const hasActiveSession = activeSessions.some(
              (s) => s.course_id === course.id
            );

            return (
              <Card key={course.id} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-1">
                      {course.course_code}
                    </h3>
                    <p className="text-gray-300 text-sm mb-2 line-clamp-2">
                      {course.course_title}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>{course.level} Level</span>
                      <span>{course.course_unit} Units</span>
                      <span>{course.semester}</span>
                    </div>
                  </div>
                  <div
                    className={`h-3 w-3 rounded-full ${
                      hasActiveSession ? "bg-green-400" : "bg-gray-500"
                    }`}
                  />
                </div>

                {/* Course Stats */}
                {courseAnalytics && (
                  <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-gray-800/50 rounded-lg">
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Students</p>
                      <p className="text-lg font-semibold text-white">
                        {courseAnalytics.total_students}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Attendance</p>
                      <p className="text-lg font-semibold text-white">
                        {Math.round(courseAnalytics.overall_attendance_rate)}%
                      </p>
                    </div>
                  </div>
                )}

                {/* Course Actions */}
                <div className="flex gap-2">
                  {hasActiveSession ? (
                    <Button
                      onClick={() => handleStopAttendance(course.id)}
                      variant="danger"
                      size="sm"
                      className="flex-1 flex items-center justify-center gap-2"
                    >
                      <AlertCircle className="h-4 w-4" />
                      Stop Attendance
                    </Button>
                  ) : (
                    <Button
                      onClick={() => handleStartAttendance(course.id)}
                      variant="success"
                      size="sm"
                      className="flex-1 flex items-center justify-center gap-2"
                    >
                      <Camera className="h-4 w-4" />
                      Start Attendance
                    </Button>
                  )}
                  <Button
                    onClick={() => setSelectedCourse(course)}
                    variant="secondary"
                    size="sm"
                    className="flex items-center justify-center"
                  >
                    <BarChart3 className="h-4 w-4" />
                  </Button>
                </div>

                {/* Class Schedule */}
                {course.class_days && (
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <p className="text-xs text-gray-400 mb-1">Schedule</p>
                    <p className="text-sm text-gray-300">
                      {course.class_days.join(", ")} • {course.class_time_start}{" "}
                      - {course.class_time_end}
                    </p>
                    {course.classroom && (
                      <p className="text-xs text-gray-400">
                        {course.classroom}
                      </p>
                    )}
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        {/* Recent Activity */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Recent Activity
          </h3>
          <div className="space-y-3">
            {activeSessions.map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse" />
                  <div>
                    <p className="text-white font-medium">
                      {session.course_code}
                    </p>
                    <p className="text-gray-400 text-sm">
                      Attendance in progress
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white text-sm">
                    {session.attendees || 0} students
                  </p>
                  <p className="text-gray-400 text-xs">
                    Started {new Date(session.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {activeSessions.length === 0 && (
              <p className="text-gray-400 text-center py-4">
                No active sessions
              </p>
            )}
          </div>
        </Card>
      </div>

      {/* Modals */}
      <CreateCourseModal
        isOpen={showCreateCourse}
        onClose={() => setShowCreateCourse(false)}
      />

      <EnrollStudentModal
        isOpen={showEnrollStudent}
        onClose={() => setShowEnrollStudent(false)}
        courses={courses}
      />

      {selectedCourse && (
        <Modal
          isOpen={!!selectedCourse}
          onClose={() => setSelectedCourse(null)}
          title={`${selectedCourse.course_code} Analytics`}
        >
          <AttendanceAnalytics course={selectedCourse} />
        </Modal>
      )}
    </div>
  );
};

export default LecturerDashboard;
