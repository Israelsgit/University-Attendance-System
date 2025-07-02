import React, { useState, useEffect } from "react";
import {
  Calendar,
  Clock,
  Filter,
  Download,
  Search,
  CheckCircle,
  XCircle,
  Edit,
  Trash2,
  Plus,
  FileText,
} from "lucide-react";
import { useAttendance } from "../hooks/useAttendance";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import Modal from "../components/common/Modal";
import { format, startOfMonth, endOfMonth, subMonths } from "date-fns";

const Attendance = () => {
  const {
    attendanceHistory,
    loadAttendanceHistory,
    manualCheckIn,
    manualCheckOut,
    requestLeave,
    isLoading,
  } = useAttendance();

  const [filters, setFilters] = useState({
    startDate: format(startOfMonth(new Date()), "yyyy-MM-dd"),
    endDate: format(endOfMonth(new Date()), "yyyy-MM-dd"),
    status: "",
    search: "",
  });

  const [showManualModal, setShowManualModal] = useState(false);
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [manualType, setManualType] = useState("check-in");
  const [manualReason, setManualReason] = useState("");
  const [leaveData, setLeaveData] = useState({
    startDate: "",
    endDate: "",
    type: "sick",
    reason: "",
  });

  useEffect(() => {
    loadAttendanceHistory(filters);
  }, [filters]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleManualSubmit = async () => {
    try {
      if (manualType === "check-in") {
        await manualCheckIn(manualReason);
      } else {
        await manualCheckOut(manualReason);
      }
      setShowManualModal(false);
      setManualReason("");
      loadAttendanceHistory(filters);
    } catch (error) {
      console.error("Manual attendance error:", error);
    }
  };

  const handleLeaveSubmit = async () => {
    try {
      await requestLeave(leaveData);
      setShowLeaveModal(false);
      setLeaveData({
        startDate: "",
        endDate: "",
        type: "sick",
        reason: "",
      });
      loadAttendanceHistory(filters);
    } catch (error) {
      console.error("Leave request error:", error);
    }
  };

  const exportToCSV = () => {
    const csvContent = [
      ["Date", "Check In", "Check Out", "Total Hours", "Status"],
      ...attendanceHistory.map((record) => [
        record.date,
        record.checkIn || "N/A",
        record.checkOut || "N/A",
        record.totalHours || 0,
        record.status,
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `attendance-${format(new Date(), "yyyy-MM-dd")}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "present":
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case "absent":
        return <XCircle className="h-5 w-5 text-red-400" />;
      case "late":
        return <Clock className="h-5 w-5 text-yellow-400" />;
      default:
        return <XCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "present":
        return "bg-green-500/20 text-green-400 border-green-500/40";
      case "absent":
        return "bg-red-500/20 text-red-400 border-red-500/40";
      case "late":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/40";
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/40";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Attendance Records
              </h1>
              <p className="text-gray-400">
                View and manage your attendance history
              </p>
            </div>

            <div className="mt-4 md:mt-0 flex flex-col sm:flex-row gap-3">
              <Button
                onClick={() => setShowLeaveModal(true)}
                variant="secondary"
                className="group"
              >
                <FileText className="h-5 w-5 mr-2 group-hover:scale-110 transition-transform" />
                Request Leave
              </Button>

              <Button
                onClick={() => {
                  setManualType("check-in");
                  setShowManualModal(true);
                }}
                variant="primary"
                className="group"
              >
                <Plus className="h-5 w-5 mr-2 group-hover:scale-110 transition-transform" />
                Manual Entry
              </Button>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Input
              label="Start Date"
              type="date"
              name="startDate"
              value={filters.startDate}
              onChange={handleFilterChange}
            />

            <Input
              label="End Date"
              type="date"
              name="endDate"
              value={filters.endDate}
              onChange={handleFilterChange}
            />

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Status
              </label>
              <select
                name="status"
                value={filters.status}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="" className="bg-gray-800">
                  All Status
                </option>
                <option value="present" className="bg-gray-800">
                  Present
                </option>
                <option value="absent" className="bg-gray-800">
                  Absent
                </option>
                <option value="late" className="bg-gray-800">
                  Late
                </option>
              </select>
            </div>

            <Input
              label="Search"
              type="text"
              name="search"
              value={filters.search}
              onChange={handleFilterChange}
              placeholder="Search records..."
              icon={Search}
            />

            <div className="flex items-end">
              <Button
                onClick={exportToCSV}
                variant="secondary"
                fullWidth
                className="group"
              >
                <Download className="h-4 w-4 mr-2 group-hover:translate-y-1 transition-transform" />
                Export
              </Button>
            </div>
          </div>
        </div>

        {/* Attendance Table */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 overflow-hidden">
          <div className="p-6 border-b border-white/20">
            <h2 className="text-xl font-semibold text-white">
              Attendance History
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-white/5">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">
                    Date
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">
                    Check In
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">
                    Check Out
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">
                    Total Hours
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">
                    Location
                  </th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-gray-300">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4">
                        <div className="h-4 bg-white/10 rounded skeleton"></div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="h-4 bg-white/10 rounded skeleton"></div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="h-4 bg-white/10 rounded skeleton"></div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="h-4 bg-white/10 rounded skeleton"></div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="h-6 w-20 bg-white/10 rounded skeleton"></div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="h-4 bg-white/10 rounded skeleton"></div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="h-8 w-16 bg-white/10 rounded skeleton"></div>
                      </td>
                    </tr>
                  ))
                ) : attendanceHistory.length > 0 ? (
                  attendanceHistory.map((record) => (
                    <tr
                      key={record.id}
                      className="hover:bg-white/5 transition-colors"
                    >
                      <td className="px-6 py-4 text-white">
                        {format(new Date(record.date), "MMM dd, yyyy")}
                      </td>
                      <td className="px-6 py-4 text-gray-300">
                        {record.checkIn
                          ? format(
                              new Date(`${record.date}T${record.checkIn}`),
                              "HH:mm"
                            )
                          : "N/A"}
                      </td>
                      <td className="px-6 py-4 text-gray-300">
                        {record.checkOut
                          ? format(
                              new Date(`${record.date}T${record.checkOut}`),
                              "HH:mm"
                            )
                          : "N/A"}
                      </td>
                      <td className="px-6 py-4 text-white font-medium">
                        {record.totalHours}h
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-sm border ${getStatusColor(
                            record.status
                          )}`}
                        >
                          {getStatusIcon(record.status)}
                          <span className="ml-2 capitalize">
                            {record.status}
                          </span>
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-300">
                        {record.location || "N/A"}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end space-x-2">
                          <button className="text-gray-400 hover:text-white p-1 rounded transition-colors">
                            <Edit className="h-4 w-4" />
                          </button>
                          <button className="text-gray-400 hover:text-red-400 p-1 rounded transition-colors">
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center">
                      <Calendar className="h-12 w-12 text-gray-500 mx-auto mb-4" />
                      <p className="text-gray-400">
                        No attendance records found
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Try adjusting your filters or date range
                      </p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Manual Entry Modal */}
      <Modal
        isOpen={showManualModal}
        onClose={() => setShowManualModal(false)}
        title={`Manual ${manualType === "check-in" ? "Check In" : "Check Out"}`}
        maxWidth="md"
      >
        <div className="space-y-6">
          <div className="flex space-x-4">
            <button
              onClick={() => setManualType("check-in")}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                manualType === "check-in"
                  ? "bg-primary-600 text-white"
                  : "bg-white/10 text-gray-300 hover:bg-white/20"
              }`}
            >
              Check In
            </button>
            <button
              onClick={() => setManualType("check-out")}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                manualType === "check-out"
                  ? "bg-primary-600 text-white"
                  : "bg-white/10 text-gray-300 hover:bg-white/20"
              }`}
            >
              Check Out
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Reason for Manual Entry
            </label>
            <textarea
              value={manualReason}
              onChange={(e) => setManualReason(e.target.value)}
              placeholder="Please provide a reason for manual entry..."
              rows={4}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              required
            />
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              onClick={() => setShowManualModal(false)}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={handleManualSubmit}
              variant="primary"
              disabled={!manualReason.trim()}
            >
              Submit Entry
            </Button>
          </div>
        </div>
      </Modal>

      {/* Leave Request Modal */}
      <Modal
        isOpen={showLeaveModal}
        onClose={() => setShowLeaveModal(false)}
        title="Request Leave"
        maxWidth="md"
      >
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Start Date"
              type="date"
              value={leaveData.startDate}
              onChange={(e) =>
                setLeaveData((prev) => ({ ...prev, startDate: e.target.value }))
              }
              required
            />

            <Input
              label="End Date"
              type="date"
              value={leaveData.endDate}
              onChange={(e) =>
                setLeaveData((prev) => ({ ...prev, endDate: e.target.value }))
              }
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Leave Type
            </label>
            <select
              value={leaveData.type}
              onChange={(e) =>
                setLeaveData((prev) => ({ ...prev, type: e.target.value }))
              }
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="sick" className="bg-gray-800">
                Sick Leave
              </option>
              <option value="vacation" className="bg-gray-800">
                Vacation
              </option>
              <option value="personal" className="bg-gray-800">
                Personal Leave
              </option>
              <option value="emergency" className="bg-gray-800">
                Emergency
              </option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Reason
            </label>
            <textarea
              value={leaveData.reason}
              onChange={(e) =>
                setLeaveData((prev) => ({ ...prev, reason: e.target.value }))
              }
              placeholder="Please provide details for your leave request..."
              rows={4}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              required
            />
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              onClick={() => setShowLeaveModal(false)}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={handleLeaveSubmit}
              variant="primary"
              disabled={
                !leaveData.startDate ||
                !leaveData.endDate ||
                !leaveData.reason.trim()
              }
            >
              Submit Request
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Attendance;
