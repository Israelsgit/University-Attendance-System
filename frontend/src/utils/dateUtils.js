import { format, formatDistanceToNow, parseISO } from "date-fns";

export const formatDate = (date, formatStr = "MMM dd, yyyy") => {
  if (!date) return "";
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return format(dateObj, formatStr);
};

export const formatDateTime = (date) => {
  if (!date) return "";
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return format(dateObj, "MMM dd, yyyy HH:mm");
};

export const formatTimeAgo = (date) => {
  if (!date) return "";
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return formatDistanceToNow(dateObj, { addSuffix: true });
};

export const getCurrentAcademicSession = () => {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1; // 1-12

  // Assuming academic year starts in September
  if (currentMonth >= 10) {
    return `${currentYear}/${currentYear + 1}`;
  } else {
    return `${currentYear - 1}/${currentYear}`;
  }
};

export const getCurrentSemester = () => {
  const currentMonth = new Date().getMonth() + 1; // 1-12

  // First semester: September to January
  // Second semester: February to June
  // Rain semester: July to August

  if (currentMonth >= 10 || currentMonth === 1) {
    return "First Semester";
  } else if (currentMonth >= 2 && currentMonth <= 6) {
    return "Second Semester";
  } else {
    return "Rain Semester";
  }
};
