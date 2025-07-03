import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { TrendingUp, Users, Calendar, Percent } from "lucide-react";
import Card from "../common/Card";

const AttendanceAnalytics = ({ course }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchAnalytics();
  }, [course]);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(
        `/api/attendance/course/${course.id}/analytics`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("attendance_token")}`,
          },
        }
      );
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400" />
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center text-gray-400 py-8">
        Failed to load analytics data
      </div>
    );
  }

  const { summary, student_statistics, session_statistics } = analytics;

  // Prepare chart data
  const attendanceDistribution = [
    { name: "Present", value: summary.present_count, color: "#22c55e" },
    { name: "Late", value: summary.late_count, color: "#f59e0b" },
    { name: "Absent", value: summary.absent_count, color: "#ef4444" },
  ];

  const sessionTrends = session_statistics.map((session) => ({
    date: new Date(session.session_date).toLocaleDateString(),
    attendance_rate: session.attendance_rate,
    attendees: session.attendees,
    topic: session.session_topic,
  }));

  const studentPerformance = student_statistics
    .sort((a, b) => b.attendance_rate - a.attendance_rate)
    .map((student) => ({
      name: student.student_name.split(" ").slice(0, 2).join(" "),
      attendance_rate: student.attendance_rate,
      present: student.present,
      late: student.late,
      absent: student.absent,
    }));

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "students", label: "Students" },
    { id: "sessions", label: "Sessions" },
  ];

  return (
    <div className="space-y-6">
      {/* Course Header */}
      <div className="text-center">
        <h3 className="text-xl font-bold text-white">{course.course_code}</h3>
        <p className="text-gray-300">{course.course_title}</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <Users className="h-6 w-6 text-blue-400 mx-auto mb-2" />
          <p className="text-2xl font-bold text-white">
            {summary.total_students}
          </p>
          <p className="text-sm text-gray-400">Students</p>
        </Card>

        <Card className="p-4 text-center">
          <Calendar className="h-6 w-6 text-green-400 mx-auto mb-2" />
          <p className="text-2xl font-bold text-white">
            {summary.total_sessions}
          </p>
          <p className="text-sm text-gray-400">Sessions</p>
        </Card>

        <Card className="p-4 text-center">
          <TrendingUp className="h-6 w-6 text-purple-400 mx-auto mb-2" />
          <p className="text-2xl font-bold text-white">
            {summary.total_attendances}
          </p>
          <p className="text-sm text-gray-400">Total Attendance</p>
        </Card>

        <Card className="p-4 text-center">
          <Percent className="h-6 w-6 text-yellow-400 mx-auto mb-2" />
          <p className="text-2xl font-bold text-white">
            {summary.overall_attendance_rate}%
          </p>
          <p className="text-sm text-gray-400">Avg Rate</p>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Attendance Distribution */}
          <Card className="p-6">
            <h4 className="text-lg font-semibold text-white mb-4">
              Attendance Distribution
            </h4>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={attendanceDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {attendanceDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>

          {/* Session Trends */}
          <Card className="p-6">
            <h4 className="text-lg font-semibold text-white mb-4">
              Session Attendance Trends
            </h4>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={sessionTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    border: "1px solid #374151",
                    borderRadius: "0.5rem",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="attendance_rate"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>
      )}

      {activeTab === "students" && (
        <Card className="p-6">
          <h4 className="text-lg font-semibold text-white mb-4">
            Student Performance
          </h4>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={studentPerformance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "0.5rem",
                }}
              />
              <Bar dataKey="attendance_rate" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>

          {/* Student List */}
          <div className="mt-6 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left text-gray-400 py-2">Student</th>
                  <th className="text-center text-gray-400 py-2">Present</th>
                  <th className="text-center text-gray-400 py-2">Late</th>
                  <th className="text-center text-gray-400 py-2">Absent</th>
                  <th className="text-center text-gray-400 py-2">Rate</th>
                </tr>
              </thead>
              <tbody>
                {student_statistics.map((student) => (
                  <tr
                    key={student.student_id}
                    className="border-b border-gray-800"
                  >
                    <td className="text-white py-3">
                      <div>
                        <p className="font-medium">{student.student_name}</p>
                        <p className="text-xs text-gray-400">
                          {student.student_identifier}
                        </p>
                      </div>
                    </td>
                    <td className="text-center text-green-400 py-3">
                      {student.present}
                    </td>
                    <td className="text-center text-yellow-400 py-3">
                      {student.late}
                    </td>
                    <td className="text-center text-red-400 py-3">
                      {student.absent}
                    </td>
                    <td className="text-center py-3">
                      <span
                        className={`font-medium ${
                          student.attendance_rate >= 75
                            ? "text-green-400"
                            : student.attendance_rate >= 60
                            ? "text-yellow-400"
                            : "text-red-400"
                        }`}
                      >
                        {student.attendance_rate}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === "sessions" && (
        <Card className="p-6">
          <h4 className="text-lg font-semibold text-white mb-4">
            Session History
          </h4>
          <div className="space-y-4">
            {session_statistics.map((session) => (
              <div
                key={session.session_id}
                className="p-4 bg-gray-800 rounded-lg"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-white font-medium">
                      {session.session_topic || "Class Session"}
                    </p>
                    <p className="text-gray-400 text-sm">
                      {new Date(session.session_date).toLocaleDateString()} •
                      {new Date(session.session_date).toLocaleTimeString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-medium">
                      {session.attendees} / {summary.total_students}
                    </p>
                    <p
                      className={`text-sm font-medium ${
                        session.attendance_rate >= 75
                          ? "text-green-400"
                          : session.attendance_rate >= 60
                          ? "text-yellow-400"
                          : "text-red-400"
                      }`}
                    >
                      {session.attendance_rate.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default AttendanceAnalytics;
