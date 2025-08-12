import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";

const DashboardChart = ({ data, type = "line" }) => {
  // Mock data if none provided
  const chartData =
    data && data.length > 0
      ? data
      : [
          { name: "Jan", attendance: 75, present: 25, absent: 8 },
          { name: "Feb", attendance: 82, present: 28, absent: 6 },
          { name: "Mar", attendance: 78, present: 26, absent: 7 },
          { name: "Apr", attendance: 85, present: 30, absent: 5 },
          { name: "May", attendance: 88, present: 32, absent: 4 },
          { name: "Jun", attendance: 84, present: 29, absent: 6 },
        ];

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
          <p className="text-white font-medium">{`${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.dataKey}: ${entry.value}${
                entry.dataKey === "attendance" ? "%" : ""
              }`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Custom grid
  const CustomGrid = (props) => (
    <CartesianGrid {...props} stroke="#334155" strokeDasharray="3 3" />
  );

  if (type === "area") {
    return (
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient
                id="attendanceGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#94A3B8", fontSize: 12 }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#94A3B8", fontSize: 12 }}
            />
            <CustomGrid />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="attendance"
              stroke="#3B82F6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#attendanceGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94A3B8", fontSize: 12 }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94A3B8", fontSize: 12 }}
          />
          <CustomGrid />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="attendance"
            stroke="#3B82F6"
            strokeWidth={3}
            dot={{ fill: "#3B82F6", strokeWidth: 2, r: 4 }}
            activeDot={{
              r: 6,
              stroke: "#3B82F6",
              strokeWidth: 2,
              fill: "#1E293B",
            }}
          />
          <Line
            type="monotone"
            dataKey="present"
            stroke="#10B981"
            strokeWidth={2}
            dot={{ fill: "#10B981", strokeWidth: 2, r: 3 }}
            activeDot={{
              r: 5,
              stroke: "#10B981",
              strokeWidth: 2,
              fill: "#1E293B",
            }}
          />
          <Line
            type="monotone"
            dataKey="absent"
            stroke="#EF4444"
            strokeWidth={2}
            dot={{ fill: "#EF4444", strokeWidth: 2, r: 3 }}
            activeDot={{
              r: 5,
              stroke: "#EF4444",
              strokeWidth: 2,
              fill: "#1E293B",
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DashboardChart;
