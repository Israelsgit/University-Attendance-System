import React from "react";

const LoadingSpinner = ({ size = "medium", color = "primary" }) => {
  const sizeClasses = {
    small: "h-4 w-4",
    medium: "h-8 w-8",
    large: "h-12 w-12",
  };

  const colorClasses = {
    primary: "border-blue-600",
    white: "border-white",
    gray: "border-gray-400",
  };

  return (
    <div className="flex items-center justify-center">
      <div
        className={`animate-spin rounded-full border-2 border-transparent ${sizeClasses[size]} ${colorClasses[color]}`}
        style={{
          borderTopColor: "currentColor",
          borderRightColor: "currentColor",
        }}
      />
    </div>
  );
};

export default LoadingSpinner;
