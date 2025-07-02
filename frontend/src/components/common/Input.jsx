import React from "react";

const Input = ({
  label,
  type = "text",
  name,
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  disabled = false,
  required = false,
  icon: Icon,
  className = "",
  ...props
}) => {
  const inputClasses = `
    w-full px-3 py-2 bg-white/10 border rounded-lg text-white placeholder-gray-400 
    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent 
    transition-all duration-200
    disabled:opacity-50 disabled:cursor-not-allowed
    ${error ? "border-red-500 focus:ring-red-500" : "border-white/20"}
    ${Icon ? "pl-10" : ""}
    ${className}
  `.trim();

  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-300">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        )}

        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          className={inputClasses}
          {...props}
        />
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
};

export default Input;
