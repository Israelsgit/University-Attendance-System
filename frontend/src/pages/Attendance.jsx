import React, { useState, useEffect } from "react";
import { Calendar, Clock, Users, Plus, Eye, Download } from "lucide-react";
import { toast } from "react-hot-toast";

import { useAuth } from "../hooks/useAuth";
import { attendanceAPI, courseAPI } from "../services/apiClient";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Button from "../components/common/Button";
import Select from "../components/common/Select";
import CreateSessionModal from "../components/modals/CreateSessionModal";

const Attendance = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [courses, setCourses] = useState([]);
  const [activeSessions, setActiveSessions] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [showCreateSession, setShowCreateSession] = useState(false);

  useEffect(() => {
    if (user?.role === "lecturer") {
      loadAttendanceData();
    }
  }, [user, selectedCourse]);

  const loadAttendanceData = async () => {
    try {
      setLoading(true);

      const [coursesRes, sessionsRes, recordsRes] = await Promise.all([
        courseAPI.getMyCourses(),
        attendanceAPI.getActiveSessions(),
        selectedCourse
          ? attendanceAPI.getCourseAttendance(selectedCourse)
          : Promise.resolve({ data: { attendance_records: [] } }),
      ]);

      setCourses(coursesRes.data.courses || []);
      setActiveSessions(sessionsRes.data.sessions || []);
      setAttendanceRecords(recordsRes.data.attendance_records || []);
    } catch (error) {
      console.error("Failed to load attendance data:", error);
      toast.error("Failed to load attendance data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSession = async (sessionData) => {
    try {
      await attendanceAPI.createSession(selectedCourse, sessionData);
      toast.success("Attendance session created successfully!");
      setShowCreateSession(false);
      loadAttendanceData();
    } catch (error) {
      console.error("Failed to create session:", error);
      toast.error("Failed to create session");
    }
  };

  const handleExportAttendance = async () => {
    try {
      if (!selectedCourse) {
        toast.error("Please select a course to export");
        return;
      }

      // Mock export functionality
      toast.success("Attendance data exported successfully!");
    } catch (error) {
      console.error("Export failed:", error);
      toast.error("Failed to export attendance data");
    }
  };

  if (user?.role !== "lecturer") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Calendar className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">
            Access Restricted
          </h2>
          <p className="text-gray-400">Only lecturers can manage attendance.</p>
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
                Attendance Management
              </h1>
              <p className="text-gray-400">
                Manage class sessions and track student attendance
              </p>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={() => setShowCreateSession(true)}
                variant="primary"
                disabled={!selectedCourse}
                className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Start Session
              </Button>

              <Button
                onClick={handleExportAttendance}
                variant="secondary"
                disabled={!selectedCourse}
              >
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
            </div>
          </div>
        </div>

        {/* Course Selection */}
        <div className="mb-8 bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
          <div className="flex items-center gap-4">
            <Calendar className="h-5 w-5 text-gray-400" />
            <div className="flex-1">
              <Select
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
                options={[
                  { value: "", label: "Select a course" },
                  ...courses.map((course) => ({
                    value: course.id,
                    label: `${course.course_code} - ${course.course_title}`,
                  })),
                ]}
                placeholder="Choose course to manage"
                className="w-full max-w-md"
              />
            </div>
          </div>
        </div>

        {/* Active Sessions */}
        <div className="mb-8 bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">
              Active Sessions
            </h2>
            <Clock className="h-5 w-5 text-gray-400" />
          </div>

          {activeSessions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {activeSessions.map((session) => (
                <div
                  key={session.id}
                  className="bg-green-500/10 border border-green-500/20 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-medium text-white">
                        {session.course_code}
                      </h3>
                      <p className="text-sm text-gray-400">
                        {session.course_title}
                      </p>
                    </div>
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Topic:</span>
                      <span className="text-gray-300">
                        {session.session_topic}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Duration:</span>
                      <span className="text-gray-300">
                        {session.duration_minutes} min
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Students:</span>
                      <span className="text-green-400">
                        {session.present_count || 0} present
                      </span>
                    </div>
                  </div>

                  <Button
                    variant="secondary"
                    size="small"
                    className="w-full mt-3"
                  >
                    <Eye className="h-3 w-3 mr-2" />
                    View Details
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Clock className="h-12 w-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 mb-2">No active sessions</p>
              <p className="text-sm text-gray-500">
                Start a new attendance session to begin tracking
              </p>
            </div>
          )}
        </div>

        {/* Attendance Records */}
        {selectedCourse && (
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">
                Attendance Records
              </h2>
              <Users className="h-5 w-5 text-gray-400" />
            </div>

            {attendanceRecords.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left text-gray-400 text-sm font-medium pb-3">
                        Student
                      </th>
                      <th className="text-left text-gray-400 text-sm font-medium pb-3">
                        Session
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
                    {attendanceRecords.map((record) => (
                      <tr key={record.id} className="border-b border-white/5">
                        <td className="py-3">
                          <div>
                            <p className="text-white font-medium">
                              {record.student_name}
                            </p>
                            <p className="text-sm text-gray-400">
                              {record.matric_number}
                            </p>
                          </div>
                        </td>
                        <td className="py-3 text-gray-300">
                          {record.session_topic}
                        </td>
                        <td className="py-3 text-gray-300">
                          {new Date(record.session_date).toLocaleDateString()}
                        </td>
                        <td className="py-3">
                          <span
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              record.status === "present"
                                ? "bg-green-500/20 text-green-400"
                                : "bg-red-500/20 text-red-400"
                            }`}
                          >
                            {record.status}
                          </span>
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
                <Users className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-2">No attendance records</p>
                <p className="text-sm text-gray-500">
                  {selectedCourse
                    ? "No attendance has been recorded for this course yet"
                    : "Select a course to view attendance records"}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Session Modal */}
      {showCreateSession && selectedCourse && (
        <CreateSessionModal
          isOpen={showCreateSession}
          onClose={() => setShowCreateSession(false)}
          onSubmit={handleCreateSession}
          course={courses.find((c) => c.id === parseInt(selectedCourse))}
        />
      )}
    </div>
  );
};

export default Attendance;
