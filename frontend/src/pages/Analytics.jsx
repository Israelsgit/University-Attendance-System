import React, { useState, useEffect } from "react";
import {
  BarChart3,
  TrendingUp,
  Calendar,
  Clock,
  Users,
  Target,
  Award,
  AlertCircle,
} from "lucide-react";
import { useAttendance } from "../hooks/useAttendance";
import AttendanceChart from "../components/charts/AttendanceChart";
import WeeklyChart from "../components/charts/WeeklyChart";
import { attendanceService } from "../services/attendance";

const Analytics = () => {
  const { weeklyStats, monthlyStats } = useAttendance();
  const [analytics, setAnalytics] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState("month");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [selectedPeriod]);

  const loadAnalytics = async () => {
    try {
      setIsLoading(true);
      const data = await attendanceService.getAnalytics(selectedPeriod);
      setAnalytics(data);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const kpiCards = [
    {
      title: "Total Hours",
      value: analytics?.totalHours || 0,
      unit: "hrs",
      icon: Clock,
      color: "primary",
      change: "+2.5%",
      trend: "up",
    },
    {
      title: "Attendance Rate",
      value: analytics?.attendanceRate || 0,
      unit: "%",
      icon: Target,
      color: "success",
      change: "+5.2%",
      trend: "up",
    },
    {
      title: "Avg Daily Hours",
      value: analytics?.avgDailyHours || 0,
      unit: "hrs",
      icon: BarChart3,
      color: "purple",
      change: "-0.3%",
      trend: "down",
    },
    {
      title: "Overtime Hours",
      value: analytics?.overtimeHours || 0,
      unit: "hrs",
      icon: TrendingUp,
      color: "orange",
      change: "+12.1%",
      trend: "up",
    },
  ];

  const getColorClasses = (color) => {
    const colors = {
      primary: "from-blue-500 to-blue-600",
      success: "from-green-500 to-green-600",
      purple: "from-purple-500 to-purple-600",
      orange: "from-orange-500 to-orange-600",
    };
    return colors[color] || colors.primary;
  };

  const getTrendColor = (trend) => {
    return trend === "up" ? "text-green-400" : "text-red-400";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Analytics Dashboard
              </h1>
              <p className="text-gray-400">
                Track your attendance patterns and performance metrics
              </p>
            </div>

            <div className="mt-4 md:mt-0">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="week" className="bg-gray-800">
                  This Week
                </option>
                <option value="month" className="bg-gray-800">
                  This Month
                </option>
                <option value="quarter" className="bg-gray-800">
                  This Quarter
                </option>
                <option value="year" className="bg-gray-800">
                  This Year
                </option>
              </select>
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {kpiCards.map((kpi, index) => {
            const IconComponent = kpi.icon;
            return (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div
                    className={`h-12 w-12 rounded-xl bg-gradient-to-r ${getColorClasses(
                      kpi.color
                    )} flex items-center justify-center group-hover:scale-110 transition-transform`}
                  >
                    <IconComponent className="h-6 w-6 text-white" />
                  </div>
                  <div
                    className={`text-sm font-medium ${getTrendColor(
                      kpi.trend
                    )}`}
                  >
                    {kpi.change}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-1">
                    {kpi.title}
                  </h3>
                  <div className="flex items-baseline">
                    <p className="text-2xl font-bold text-white">
                      {isLoading ? (
                        <div className="h-8 w-16 bg-white/10 rounded skeleton"></div>
                      ) : (
                        `${kpi.value}${kpi.unit}`
                      )}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Daily Trend Chart */}
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">
                Daily Attendance Trend
              </h2>
              <div className="flex items-center space-x-2">
                <div className="h-3 w-3 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-gray-400">Hours</span>
                <div className="h-3 w-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-400">Rate</span>
              </div>
            </div>

            {isLoading ? (
              <div className="h-80 bg-white/5 rounded-lg animate-pulse"></div>
            ) : (
              <AttendanceChart
                data={analytics?.trends?.daily || []}
                type="area"
              />
            )}
          </div>

          {/* Weekly Performance */}
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">
                Weekly Performance
              </h2>
              <select className="bg-white/10 border border-white/20 rounded-lg px-3 py-1 text-white text-sm">
                <option value="current" className="bg-gray-800">
                  Current Week
                </option>
                <option value="previous" className="bg-gray-800">
                  Previous Week
                </option>
              </select>
            </div>

            {isLoading ? (
              <div className="h-80 bg-white/5 rounded-lg animate-pulse"></div>
            ) : (
              <WeeklyChart data={weeklyStats?.weeklyData || []} />
            )}
          </div>
        </div>

        {/* Performance Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Attendance Patterns */}
          <div className="lg:col-span-2 bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <h2 className="text-xl font-semibold text-white mb-6">
              Attendance Patterns
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded-full bg-green-500/20 flex items-center justify-center mr-4">
                    <Award className="h-5 w-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Best Streak</p>
                    <p className="text-gray-400 text-sm">
                      Consecutive days present
                    </p>
                  </div>
                </div>
                <span className="text-2xl font-bold text-white">
                  {analytics?.bestStreak || 15} days
                </span>
              </div>

              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded-full bg-blue-500/20 flex items-center justify-center mr-4">
                    <Clock className="h-5 w-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">
                      Average Check-in Time
                    </p>
                    <p className="text-gray-400 text-sm">
                      Your typical arrival time
                    </p>
                  </div>
                </div>
                <span className="text-2xl font-bold text-white">9:15 AM</span>
              </div>

              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded-full bg-purple-500/20 flex items-center justify-center mr-4">
                    <TrendingUp className="h-5 w-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">
                      Most Productive Day
                    </p>
                    <p className="text-gray-400 text-sm">
                      Highest average hours
                    </p>
                  </div>
                </div>
                <span className="text-2xl font-bold text-white">Wednesday</span>
              </div>

              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded-full bg-orange-500/20 flex items-center justify-center mr-4">
                    <AlertCircle className="h-5 w-5 text-orange-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Late Arrivals</p>
                    <p className="text-gray-400 text-sm">This month</p>
                  </div>
                </div>
                <span className="text-2xl font-bold text-white">
                  {analytics?.lateArrivals || 3}
                </span>
              </div>
            </div>
          </div>

          {/* Goals & Achievements */}
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
            <h2 className="text-xl font-semibold text-white mb-6">
              Goals & Progress
            </h2>

            <div className="space-y-6">
              {/* Attendance Goal */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-medium">
                    Monthly Attendance
                  </span>
                  <span className="text-sm text-gray-400">95%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: "95%" }}
                  ></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  Goal: 90% • Achieved!
                </p>
              </div>

              {/* Hours Goal */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-medium">Monthly Hours</span>
                  <span className="text-sm text-gray-400">160h / 170h</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: "94%" }}
                  ></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">10 hours remaining</p>
              </div>

              {/* Streak Goal */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-medium">
                    Perfect Week Streak
                  </span>
                  <span className="text-sm text-gray-400">3 / 4 weeks</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: "75%" }}
                  ></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  1 more week to achieve monthly goal
                </p>
              </div>

              {/* Achievement Badges */}
              <div className="pt-4 border-t border-white/20">
                <h3 className="text-white font-medium mb-3">
                  Recent Achievements
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-yellow-500/20 border border-yellow-500/40 rounded-lg p-3 text-center">
                    <Award className="h-6 w-6 text-yellow-400 mx-auto mb-1" />
                    <p className="text-xs text-yellow-300">Perfect Week</p>
                  </div>
                  <div className="bg-green-500/20 border border-green-500/40 rounded-lg p-3 text-center">
                    <Target className="h-6 w-6 text-green-400 mx-auto mb-1" />
                    <p className="text-xs text-green-300">95% Month</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Statistics */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-6">
            Detailed Statistics
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-3">
                <Calendar className="h-8 w-8 text-blue-400" />
              </div>
              <h3 className="text-white font-semibold mb-1">
                Total Days Worked
              </h3>
              <p className="text-3xl font-bold text-blue-400">
                {isLoading ? (
                  <div className="h-8 w-12 bg-white/10 rounded skeleton mx-auto"></div>
                ) : (
                  analytics?.totalDays || 22
                )}
              </p>
              <p className="text-sm text-gray-400">This month</p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-3">
                <Clock className="h-8 w-8 text-green-400" />
              </div>
              <h3 className="text-white font-semibold mb-1">
                On-Time Arrivals
              </h3>
              <p className="text-3xl font-bold text-green-400">
                {isLoading ? (
                  <div className="h-8 w-12 bg-white/10 rounded skeleton mx-auto"></div>
                ) : (
                  `${Math.round(
                    (((analytics?.totalDays || 22) -
                      (analytics?.lateArrivals || 3)) /
                      (analytics?.totalDays || 22)) *
                      100
                  )}%`
                )}
              </p>
              <p className="text-sm text-gray-400">Success rate</p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="h-8 w-8 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-1">
                Productivity Score
              </h3>
              <p className="text-3xl font-bold text-purple-400">
                {isLoading ? (
                  <div className="h-8 w-12 bg-white/10 rounded skeleton mx-auto"></div>
                ) : (
                  "8.7/10"
                )}
              </p>
              <p className="text-sm text-gray-400">
                Based on hours & attendance
              </p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-orange-500/20 flex items-center justify-center mx-auto mb-3">
                <Users className="h-8 w-8 text-orange-400" />
              </div>
              <h3 className="text-white font-semibold mb-1">Team Ranking</h3>
              <p className="text-3xl font-bold text-orange-400">
                {isLoading ? (
                  <div className="h-8 w-12 bg-white/10 rounded skeleton mx-auto"></div>
                ) : (
                  "#3"
                )}
              </p>
              <p className="text-sm text-gray-400">Out of 25 members</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
