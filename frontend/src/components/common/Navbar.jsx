import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  GraduationCap,
  LayoutDashboard,
  BookOpen,
  Users,
  BarChart3,
  Calendar,
  Camera,
  User,
  Settings,
  LogOut,
  Menu,
  X,
  Shield,
  Bell,
} from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { toast } from "react-hot-toast";

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  // Don't show navbar on auth pages
  const authPages = [
    "/login",
    "/register",
    "/register/student",
    "/register/lecturer",
  ];
  if (authPages.some((page) => location.pathname.startsWith(page))) {
    return null;
  }

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Logged out successfully");
      navigate("/login");
    } catch (error) {
      console.error("Logout error:", error);
      toast.error("Error logging out");
    }
  };

  // Navigation items based on user role
  const getNavigationItems = () => {
    if (!user) return [];

    const commonItems = [
      {
        name: "Dashboard",
        href: "/dashboard",
        icon: LayoutDashboard,
        current: location.pathname === "/dashboard",
      },
      {
        name: "Profile",
        href: "/profile",
        icon: User,
        current: location.pathname === "/profile",
      },
    ];

    if (user.role === "student") {
      return [
        ...commonItems,
        {
          name: "My Courses",
          href: "/my-courses",
          icon: BookOpen,
          current: location.pathname === "/my-courses",
        },
        {
          name: "My Attendance",
          href: "/my-attendance",
          icon: Calendar,
          current: location.pathname === "/my-attendance",
        },
        {
          name: "Face Recognition",
          href: "/face-recognition",
          icon: Camera,
          current: location.pathname === "/face-recognition",
        },
      ];
    } else if (user.role === "lecturer") {
      return [
        ...commonItems,
        {
          name: "Courses",
          href: "/courses",
          icon: BookOpen,
          current: location.pathname === "/courses",
        },
        {
          name: "Students",
          href: "/students",
          icon: Users,
          current: location.pathname === "/students",
        },
        {
          name: "Attendance",
          href: "/attendance",
          icon: Calendar,
          current: location.pathname === "/attendance",
        },
        {
          name: "Analytics",
          href: "/analytics",
          icon: BarChart3,
          current: location.pathname === "/analytics",
        },
      ];
    }

    return commonItems;
  };

  const navigationItems = getNavigationItems();

  if (!user) {
    return null;
  }

  return (
    <nav className="bg-slate-900/95 backdrop-blur-md border-b border-slate-800 fixed top-0 left-0 right-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and brand */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <GraduationCap className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white hidden sm:block">
                AttendanceAI
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  item.current
                    ? "bg-blue-600 text-white"
                    : "text-gray-300 hover:bg-slate-800 hover:text-white"
                }`}
              >
                <item.icon className="h-4 w-4 mr-2" />
                {item.name}
              </Link>
            ))}
          </div>

          {/* User menu and mobile menu button */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="text-gray-400 hover:text-white transition-colors">
              <Bell className="h-5 w-5" />
            </button>

            {/* User Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {user.full_name?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium">{user.full_name}</p>
                  <div className="flex items-center text-xs text-gray-400">
                    {user.role === "lecturer" && (
                      <Shield className="h-3 w-3 mr-1" />
                    )}
                    <span className="capitalize">{user.role}</span>
                  </div>
                </div>
              </button>

              {/* Profile Dropdown */}
              {isProfileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-slate-800 rounded-lg shadow-lg border border-slate-700 py-1 z-50">
                  <div className="px-4 py-2 border-b border-slate-700">
                    <p className="text-sm font-medium text-white">
                      {user.full_name}
                    </p>
                    <p className="text-xs text-gray-400">{user.email}</p>
                    {user.role === "student" && user.matric_number && (
                      <p className="text-xs text-gray-500">
                        {user.matric_number}
                      </p>
                    )}
                    {user.role === "lecturer" && user.staff_id && (
                      <p className="text-xs text-gray-500">{user.staff_id}</p>
                    )}
                  </div>

                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-slate-700 hover:text-white transition-colors"
                    onClick={() => setIsProfileMenuOpen(false)}
                  >
                    <User className="h-4 w-4 inline mr-2" />
                    Profile Settings
                  </Link>

                  {user.role === "lecturer" && (
                    <Link
                      to="/analytics"
                      className="block px-4 py-2 text-sm text-gray-300 hover:bg-slate-700 hover:text-white transition-colors"
                      onClick={() => setIsProfileMenuOpen(false)}
                    >
                      <BarChart3 className="h-4 w-4 inline mr-2" />
                      System Analytics
                    </Link>
                  )}

                  <button
                    onClick={() => {
                      setIsProfileMenuOpen(false);
                      // Add settings modal or navigate to settings
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-slate-700 hover:text-white transition-colors"
                  >
                    <Settings className="h-4 w-4 inline mr-2" />
                    Settings
                  </button>

                  <hr className="border-slate-700 my-1" />

                  <button
                    onClick={() => {
                      setIsProfileMenuOpen(false);
                      handleLogout();
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-slate-700 hover:text-red-300 transition-colors"
                  >
                    <LogOut className="h-4 w-4 inline mr-2" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden text-gray-400 hover:text-white transition-colors"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-slate-800 border-t border-slate-700">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  item.current
                    ? "bg-blue-600 text-white"
                    : "text-gray-300 hover:bg-slate-700 hover:text-white"
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <item.icon className="h-4 w-4 inline mr-2" />
                {item.name}
              </Link>
            ))}

            {/* Role indicator */}
            <div className="px-3 py-2 border-t border-slate-600 mt-2">
              <div className="flex items-center text-xs text-gray-400">
                {user.role === "lecturer" && (
                  <Shield className="h-3 w-3 mr-1" />
                )}
                <span className="capitalize">{user.role}</span>
                {user.role === "lecturer" && (
                  <span className="ml-1">• Admin Access</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Click outside to close profile menu */}
      {isProfileMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsProfileMenuOpen(false)}
        />
      )}
    </nav>
  );
};

export default Navbar;
