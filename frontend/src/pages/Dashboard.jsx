import React, { useState, useEffect } from "react";
import {
  Clock,
  Users,
  Calendar,
  TrendingUp,
  CheckCircle,
  XCircle,
  Activity,
  MapPin,
  Timer,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useAttendance } from "../hooks/useAttendance";
import AttendanceChart from "../components/charts/AttendanceChart";
import WeeklyChart from "../components/charts/WeeklyChart";
import CameraCapture from "../components/camera/CameraCapture";
import Button from "../components/common/Button";
import { format } from "date-fns";

const Dashboard = () => {
  const { user } = useAuth();
  const { todayAttendance, weeklyStats, checkIn, checkOut, isLoading } =
    useAttendance();

  const [currentTime, setCurrentTime] = useState(new Date());
  const [showCamera, setShowCamera] = useState(false);
  const [isCheckingIn, setIsCheckingIn] = useState(false);

  // Update current time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleFaceRecognition = async (faceData) => {
    try {
      setIsCheckingIn(true);

      if (!todayAttendance?.checkIn) {
        await checkIn(faceData);
      } else if (!todayAttendance?.checkOut) {
        await checkOut(faceData);
      }

      setShowCamera(false);
    } catch (error) {
      console.error("Face recognition error:", error);
    } finally {
      setIsCheckingIn(false);
    }
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 17) return "Good Afternoon";
    return "Good Evening";
  };

  const getWorkingHours = () => {
    if (!todayAttendance?.checkIn) return "0h 0m";

    const checkInTime = new Date(todayAttendance.checkIn);
    const endTime = todayAttendance.checkOut
      ? new Date(todayAttendance.checkOut)
      : currentTime;

    const diffMs = endTime - checkInTime;
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    return `${hours}h ${minutes}m`;
  };

  const statsCards = [
    {
      title: "Today's Status",
      value: todayAttendance?.checkIn ? "Present" : "Absent",
      icon: todayAttendance?.checkIn ? CheckCircle : XCircle,
      color: todayAttendance?.checkIn ? "success" : "danger",
      subtitle: todayAttendance?.checkIn
        ? `Checked in at ${format(new Date(todayAttendance.checkIn), "HH:mm")}`
        : "Not checked in yet",
    },
    {
      title: "Working Hours",
      value: getWorkingHours(),
      icon: Clock,
      color: "primary",
      subtitle: "Today's total",
    },
    {
      title: "This Week",
      value: `${weeklyStats?.presentDays || 0}/5`,
      icon: Calendar,
      color: "purple",
      subtitle: "Days present",
    },
    {
      title: "Monthly Average",
      value: `${weeklyStats?.avgHours || 0}h`,
      icon: TrendingUp,
      color: "orange",
      subtitle: "Hours per day",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                {getGreeting()}, {user?.name}!
              </h1>
              <p className="text-gray-400 flex items-center">
                <MapPin className="h-4 w-4 mr-2" />
                {format(currentTime, "EEEE, MMMM do, yyyy")} •{" "}
                {format(currentTime, "HH:mm:ss")}
              </p>
            </div>

            <div className="mt-4 md:mt-0 flex flex-col sm:flex-row gap-3">
              <Button
                onClick={() => setShowCamera(true)}
                variant={
                  !todayAttendance?.checkIn
                    ? "success"
                    : todayAttendance?.checkOut
                    ? "secondary"
                    : "danger"
                }
                disabled={todayAttendance?.checkOut}
                className="group"
              >
                <Activity className="h-5 w-5 mr-2 group-hover:scale-110 transition-transform" />
                {!todayAttendance?.checkIn
                  ? "Check In"
                  : todayAttendance?.checkOut
                  ? "Already Checked Out"
                  : "Check Out"}
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statsCards.map((stat, index) => {
            const IconComponent = stat.icon;
            const colorClasses = {
              primary: "from-blue-500 to-blue-600",
              success: "from-green-500 to-green-600",
              danger: "from-red-500 to-red-600",
              purple: "from-purple-500 to-purple-600",
              orange: "from-orange-500 to-orange-600",
            };

            return (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div
                    className={`h-12 w-12 rounded-xl bg-gradient-to-r ${
                      colorClasses[stat.color]
                    } flex items-center justify-center group-hover:scale-110 transition-transform`}
                  >
                    <IconComponent className="h-6 w-6 text-white" />
                  </div>
                  <div className="text-right">
                    <h3 className="text-sm font-medium text-gray-400">
                      {stat.title}
                    </h3>
                    <p className="text-2xl font-bold text-white mt-1">
                      {stat.value}
                    </p>
                  </div>
                </div>
                <p className="text-sm text-gray-400">{stat.subtitle}</p>
              </div>
            );
          })}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Weekly Attendance Chart */}
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">
                Weekly Overview
              </h2>
              <div className="flex items-center space-x-2">
                <div className="h-3 w-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-400">Present</span>
                <div className="h-3 w-3 bg-red-500 rounded-full"></div>
                <span className="text-sm text-gray-400">Absent</span>
              </div>
            </div>
            <WeeklyChart data={weeklyStats?.weeklyData || []} />
          </div>

          {/* Monthly Trend Chart */}
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">
                Monthly Trend
              </h2>
              <select className="bg-white/10 border border-white/20 rounded-lg px-3 py-1 text-white text-sm">
                <option value="hours" className="bg-gray-800">
                  Working Hours
                </option>
                <option value="attendance" className="bg-gray-800">
                  Attendance Rate
                </option>
              </select>
            </div>
            <AttendanceChart data={weeklyStats?.monthlyData || []} />
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-6">
            Recent Activity
          </h2>
          <div className="space-y-4">
            {weeklyStats?.recentActivity?.map((activity, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10"
              >
                <div className="flex items-center">
                  <div
                    className={`h-10 w-10 rounded-full flex items-center justify-center ${
                      activity.type === "check-in"
                        ? "bg-green-500/20 text-green-400"
                        : "bg-red-500/20 text-red-400"
                    }`}
                  >
                    {activity.type === "check-in" ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : (
                      <XCircle className="h-5 w-5" />
                    )}
                  </div>
                  <div className="ml-4">
                    <p className="text-white font-medium">
                      {activity.type === "check-in"
                        ? "Checked In"
                        : "Checked Out"}
                    </p>
                    <p className="text-gray-400 text-sm">{activity.date}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white font-medium">{activity.time}</p>
                  <p className="text-gray-400 text-sm">{activity.location}</p>
                </div>
              </div>
            )) || (
              <div className="text-center py-8">
                <Timer className="h-12 w-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400">No recent activity</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Camera Modal */}
      {showCamera && (
        <CameraCapture
          onCapture={handleFaceRecognition}
          onClose={() => setShowCamera(false)}
          isProcessing={isCheckingIn}
          mode={!todayAttendance?.checkIn ? "check-in" : "check-out"}
        />
      )}
    </div>
  );
};

export default Dashboard;
