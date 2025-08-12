import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const AttendanceChart = ({ data, type = "bar" }) => {
  // Mock data if none provided
  const chartData =
    data && data.length > 0
      ? data
      : [
          { course: "CSC 438", present: 10, absent: 2, percentage: 83.3 },
          { course: "CSC 426", present: 8, absent: 3, percentage: 72.7 },
          { course: "CSC 412", present: 12, absent: 1, percentage: 92.3 },
          { course: "CSC 408", present: 9, absent: 2, percentage: 81.8 },
        ];

  // Pie chart data for overall attendance
  const pieData = [
    { name: "Present", value: 85, color: "#10B981" },
    { name: "Absent", value: 15, color: "#EF4444" },
  ];

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
          <p className="text-white font-medium">{`${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value}`}
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

  if (type === "pie") {
    return (
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={5}
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
                      <p className="text-white font-medium">
                        {payload[0].name}
                      </p>
                      <p
                        className="text-sm"
                        style={{ color: payload[0].payload.color }}
                      >
                        {`${payload[0].value}%`}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
          </PieChart>
        </ResponsiveContainer>

        {/* Legend */}
        <div className="flex justify-center gap-4 mt-4">
          {pieData.map((item, index) => (
            <div key={index} className="flex items-center">
              <div
                className="w-3 h-3 rounded-full mr-2"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-gray-300">{item.name}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <XAxis
            dataKey="course"
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
          <Bar
            dataKey="present"
            name="Present"
            fill="#10B981"
            radius={[4, 4, 0, 0]}
          />
          <Bar
            dataKey="absent"
            name="Absent"
            fill="#EF4444"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AttendanceChart;
