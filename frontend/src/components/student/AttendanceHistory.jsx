import React from "react";
import {
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
} from "lucide-react";
import Card from "../common/Card";

const AttendanceHistory = ({ attendance }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case "present":
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case "late":
        return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case "absent":
        return <XCircle className="h-4 w-4 text-red-400" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "present":
        return "text-green-400";
      case "late":
        return "text-yellow-400";
      case "absent":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  if (!attendance || attendance.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Recent Attendance
        </h3>
        <div className="text-center text-gray-400 py-8">
          <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No attendance records found</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-white mb-4">
        Recent Attendance
      </h3>
      <div className="space-y-3">
        {attendance.map((record) => (
          <div
            key={record.id}
            className="flex items-center justify-between p-3 bg-gray-800 rounded-lg"
          >
            <div className="flex items-center gap-3">
              {getStatusIcon(record.status)}
              <div>
                <p className="text-white font-medium">{record.course_code}</p>
                <p className="text-gray-400 text-sm">{record.course_title}</p>
                {record.session_topic && (
                  <p className="text-gray-500 text-xs">
                    {record.session_topic}
                  </p>
                )}
              </div>
            </div>

            <div className="text-right">
              <p
                className={`font-medium capitalize ${getStatusColor(
                  record.status
                )}`}
              >
                {record.status}
              </p>
              <p className="text-gray-400 text-sm">
                {new Date(record.marked_at).toLocaleDateString()}
              </p>
              <p className="text-gray-500 text-xs">
                {new Date(record.marked_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default AttendanceHistory;
