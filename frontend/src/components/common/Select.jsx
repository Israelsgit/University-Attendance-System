import React from "react";
import { ChevronDown } from "lucide-react";

const Select = ({
  label,
  name,
  value,
  onChange,
  options = [],
  placeholder = "Select an option",
  error,
  required = false,
  disabled = false,
  className = "",
  ...props
}) => {
  return (
    <div className={className}>
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        <select
          id={name}
          name={name}
          value={value}
          onChange={onChange}
          disabled={disabled}
          className={`
            w-full px-3 py-2 bg-slate-700 border rounded-lg text-white placeholder-gray-400
            focus:ring-2 focus:ring-blue-500 focus:border-transparent
            appearance-none cursor-pointer
            ${disabled ? "opacity-50 cursor-not-allowed" : ""}
            ${error ? "border-red-500 focus:ring-red-500" : "border-slate-600"}
          `}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>

        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
      </div>

      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  );
};

export default Select;
