import React from "react";
import { Link } from "react-router-dom";
import { Home, ArrowLeft, Search } from "lucide-react";
import Button from "../components/common/Button";

const NotFound = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        {/* 404 Number */}
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
            404
          </h1>
        </div>

        {/* Content */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Page Not Found</h2>
          <p className="text-gray-400 mb-6">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        {/* Search Icon */}
        <div className="mb-8">
          <div className="w-16 h-16 bg-white/10 backdrop-blur-lg rounded-full flex items-center justify-center mx-auto border border-white/20">
            <Search className="h-8 w-8 text-gray-400" />
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-4">
          <Link to="/dashboard">
            <Button
              variant="primary"
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              <Home className="h-4 w-4 mr-2" />
              Go to Dashboard
            </Button>
          </Link>

          <button
            onClick={() => window.history.back()}
            className="w-full flex items-center justify-center px-4 py-2 text-gray-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </button>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            Need help? Contact your system administrator.
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
