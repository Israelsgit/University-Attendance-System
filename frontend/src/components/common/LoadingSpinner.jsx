import React from "react";

const LoadingSpinner = ({
  size = "medium",
  color = "primary",
  className = "",
  ...props
}) => {
  const sizeClasses = {
    small: "h-4 w-4",
    medium: "h-6 w-6",
    large: "h-8 w-8",
    xl: "h-12 w-12",
  };

  const colorClasses = {
    primary: "border-primary-500",
    white: "border-white",
    gray: "border-gray-500",
    success: "border-green-500",
    danger: "border-red-500",
  };

  return (
    <div
      className={`
        animate-spin rounded-full border-2 border-transparent
        ${sizeClasses[size]}
        ${colorClasses[color]}
        border-t-current
        ${className}
      `}
      {...props}
    />
  );
};

export default LoadingSpinner;
