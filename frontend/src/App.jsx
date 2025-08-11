import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "./context/AuthContext";
import { AttendanceProvider } from "./context/AttendanceContext";
import { CourseProvider } from "./context/CourseContext";
import { useAuth } from "./hooks/useAuth";

// Pages
import Login from "./pages/auth/Login";
import StudentRegister from "./pages/auth/StudentRegister";
import LecturerRegister from "./pages/auth/LecturerRegister";
import LecturerDashboard from "./pages/LecturerDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import Profile from "./pages/Profile";
import Analytics from "./pages/Analytics";
import Attendance from "./pages/Attendance";
import FaceRecognition from "./pages/FaceRecognition";
import NotFound from "./pages/NotFound";

// Components
import Navbar from "./components/common/Navbar";
import LoadingSpinner from "./components/common/LoadingSpinner";

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check role requirement
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return user ? <Navigate to="/dashboard" replace /> : children;
};

// Layout Component
const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Navbar />
      <main className="pt-16">{children}</main>
    </div>
  );
};

// Role-based Dashboard Route
const DashboardRoute = () => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  // Lecturers get full management dashboard
  if (user.role === "lecturer") {
    return <LecturerDashboard />;
  }
  // Students get simplified dashboard
  else if (user.role === "student") {
    return <StudentDashboard />;
  }
  // Fallback to login
  else {
    return <Navigate to="/login" replace />;
  }
};

// Analytics Route (Lecturer Only)
const AnalyticsRoute = () => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  // Only lecturers can access analytics
  if (user.role !== "lecturer") {
    return <Navigate to="/dashboard" replace />;
  }

  return <Analytics />;
};

// Attendance Management Route (Lecturer Only)
const AttendanceManagementRoute = () => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  // Only lecturers can manage attendance
  if (user.role !== "lecturer") {
    return <Navigate to="/dashboard" replace />;
  }

  return <Attendance />;
};

// Main App Component
function AppContent() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />

          <Route
            path="/register/student"
            element={
              <PublicRoute>
                <StudentRegister />
              </PublicRoute>
            }
          />

          <Route
            path="/register/lecturer"
            element={
              <PublicRoute>
                <LecturerRegister />
              </PublicRoute>
            }
          />

          {/* Redirect old register route */}
          <Route
            path="/register"
            element={<Navigate to="/register/student" replace />}
          />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardRoute />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Layout>
                  <Profile />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/face-recognition"
            element={
              <ProtectedRoute>
                <Layout>
                  <FaceRecognition />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Lecturer Only Routes */}
          <Route
            path="/analytics"
            element={
              <ProtectedRoute requiredRole="lecturer">
                <Layout>
                  <AnalyticsRoute />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/attendance"
            element={
              <ProtectedRoute requiredRole="lecturer">
                <Layout>
                  <AttendanceManagementRoute />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/courses"
            element={
              <ProtectedRoute requiredRole="lecturer">
                <Layout>
                  <LecturerDashboard />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/students"
            element={
              <ProtectedRoute requiredRole="lecturer">
                <Layout>
                  <LecturerDashboard />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Student Only Routes */}
          <Route
            path="/my-attendance"
            element={
              <ProtectedRoute requiredRole="student">
                <Layout>
                  <StudentDashboard />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/my-courses"
            element={
              <ProtectedRoute requiredRole="student">
                <Layout>
                  <StudentDashboard />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Default Routes */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* 404 Route */}
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: "rgba(15, 23, 42, 0.95)",
              color: "#ffffff",
              border: "1px solid rgba(99, 102, 241, 0.2)",
              borderRadius: "12px",
              backdropFilter: "blur(16px)",
            },
            success: {
              iconTheme: {
                primary: "#10B981",
                secondary: "#ffffff",
              },
            },
            error: {
              iconTheme: {
                primary: "#EF4444",
                secondary: "#ffffff",
              },
            },
            loading: {
              iconTheme: {
                primary: "#6366F1",
                secondary: "#ffffff",
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

// App wrapper with providers
function App() {
  return (
    <AuthProvider>
      <CourseProvider>
        <AttendanceProvider>
          <AppContent />
        </AttendanceProvider>
      </CourseProvider>
    </AuthProvider>
  );
}

export default App;
