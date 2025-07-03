export const calculateAttendanceRate = (present, total) => {
  if (total === 0) return 0;
  return Math.round((present / total) * 100);
};

export const getAttendanceStatus = (rate) => {
  if (rate >= 75) return { status: "good", color: "green" };
  if (rate >= 60) return { status: "warning", color: "yellow" };
  return { status: "poor", color: "red" };
};

export const groupAttendanceByDate = (attendanceRecords) => {
  const grouped = {};

  attendanceRecords.forEach((record) => {
    const date = new Date(record.marked_at).toDateString();
    if (!grouped[date]) {
      grouped[date] = [];
    }
    grouped[date].push(record);
  });

  return grouped;
};

export const calculateWeeklyStats = (attendanceRecords) => {
  const now = new Date();
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  const weeklyRecords = attendanceRecords.filter(
    (record) => new Date(record.marked_at) >= oneWeekAgo
  );

  const present = weeklyRecords.filter((r) => r.status === "present").length;
  const late = weeklyRecords.filter((r) => r.status === "late").length;
  const total = weeklyRecords.length;

  return {
    present,
    late,
    total,
    rate: calculateAttendanceRate(present + late, total),
  };
};
