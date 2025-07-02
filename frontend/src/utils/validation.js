import { VALIDATION_RULES, ERROR_MESSAGES } from "./constants";

// Base validation function
const createValidator = (validationFn, errorMessage) => (value) => {
  const isValid = validationFn(value);
  return {
    isValid,
    error: isValid ? null : errorMessage,
  };
};

// Individual field validators
export const validators = {
  required: (message = "This field is required") =>
    createValidator(
      (value) => value !== null && value !== undefined && value !== "",
      message
    ),

  email: (message = "Please enter a valid email address") =>
    createValidator(
      (value) => !value || VALIDATION_RULES.EMAIL.test(value),
      message
    ),

  phone: (message = "Please enter a valid phone number") =>
    createValidator(
      (value) =>
        !value || VALIDATION_RULES.PHONE.test(value.replace(/\s/g, "")),
      message
    ),

  minLength: (min, message = `Must be at least ${min} characters`) =>
    createValidator((value) => !value || value.length >= min, message),

  maxLength: (max, message = `Must be no more than ${max} characters`) =>
    createValidator((value) => !value || value.length <= max, message),

  pattern: (regex, message = "Invalid format") =>
    createValidator((value) => !value || regex.test(value), message),

  match: (compareValue, message = "Values do not match") =>
    createValidator((value) => value === compareValue, message),

  password: (message = "Password must meet requirements") =>
    createValidator((value) => {
      if (!value) return false;
      const rules = VALIDATION_RULES.PASSWORD;

      const checks = {
        minLength: value.length >= rules.MIN_LENGTH,
        maxLength: value.length <= rules.MAX_LENGTH,
        hasUppercase: rules.REQUIRE_UPPERCASE ? /[A-Z]/.test(value) : true,
        hasLowercase: rules.REQUIRE_LOWERCASE ? /[a-z]/.test(value) : true,
        hasNumbers: rules.REQUIRE_NUMBERS ? /\d/.test(value) : true,
        hasSpecialChar: rules.REQUIRE_SPECIAL
          ? /[!@#$%^&*(),.?":{}|<>]/.test(value)
          : true,
      };

      return Object.values(checks).every((check) => check);
    }, message),

  employeeId: (message = "Please enter a valid employee ID") =>
    createValidator((value) => {
      if (!value) return false;
      const rules = VALIDATION_RULES.EMPLOYEE_ID;
      return (
        value.length >= rules.MIN_LENGTH &&
        value.length <= rules.MAX_LENGTH &&
        rules.PATTERN.test(value)
      );
    }, message),

  date: (message = "Please enter a valid date") =>
    createValidator((value) => !value || !isNaN(Date.parse(value)), message),

  dateRange: (
    startDate,
    endDate,
    message = "End date must be after start date"
  ) =>
    createValidator(() => {
      if (!startDate || !endDate) return true;
      return new Date(endDate) >= new Date(startDate);
    }, message),

  fileSize: (
    maxSizeInBytes,
    message = `File size must be less than ${maxSizeInBytes / 1024 / 1024}MB`
  ) => createValidator((file) => !file || file.size <= maxSizeInBytes, message),

  fileType: (allowedTypes, message = "Invalid file type") =>
    createValidator(
      (file) => !file || allowedTypes.includes(file.type),
      message
    ),

  number: (message = "Please enter a valid number") =>
    createValidator((value) => !value || !isNaN(Number(value)), message),

  positiveNumber: (message = "Please enter a positive number") =>
    createValidator((value) => !value || Number(value) >= 0, message),

  url: (message = "Please enter a valid URL") =>
    createValidator((value) => {
      if (!value) return true;
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    }, message),
};

// Validation schema builder
export class ValidationSchema {
  constructor() {
    this.rules = {};
  }

  field(fieldName) {
    this.currentField = fieldName;
    this.rules[fieldName] = [];
    return this;
  }

  required(message) {
    if (this.currentField) {
      this.rules[this.currentField].push(validators.required(message));
    }
    return this;
  }

  email(message) {
    if (this.currentField) {
      this.rules[this.currentField].push(validators.email(message));
    }
    return this;
  }

  phone(message) {
    if (this.currentField) {
      this.rules[this.currentField].push(validators.phone(message));
    }
    return this;
  }

  minLength(min, message) {
    if (this.currentField) {
      this.rules[this.currentField].push(validators.minLength(min, message));
    }
    return this;
  }

  maxLength(max, message) {
    if (this.currentField) {
      this.rules[this.currentField].push(validators.maxLength(max, message));
    }
    return this;
  }

  pattern(regex, message) {
    if (this.currentField) {
      this.rules[this.currentField].push(validators.pattern(regex, message));
    }
    return this;
  }

  password(message) {
    if (this.currentField) {
      this.rules[this.currentField].push(validators.password(message));
    }
    return this;
  }

  employeeId(message) {
    if (this.currentField) {
      this.rules[this.currentField].push(validators.employeeId(message));
    }
    return this;
  }

  custom(validatorFn, message) {
    if (this.currentField) {
      this.rules[this.currentField].push(createValidator(validatorFn, message));
    }
    return this;
  }

  validate(data) {
    const errors = {};
    let isValid = true;

    Object.entries(this.rules).forEach(([fieldName, fieldRules]) => {
      const fieldValue = data[fieldName];

      for (const rule of fieldRules) {
        const result = rule(fieldValue);
        if (!result.isValid) {
          errors[fieldName] = result.error;
          isValid = false;
          break; // Stop at first error for this field
        }
      }
    });

    return { isValid, errors };
  }
}

// Pre-built validation schemas for common forms
export const validationSchemas = {
  login: new ValidationSchema()
    .field("email")
    .required("Email is required")
    .email()
    .field("password")
    .required("Password is required"),

  register: new ValidationSchema()
    .field("name")
    .required("Full name is required")
    .minLength(2, "Name must be at least 2 characters")
    .maxLength(50, "Name must be no more than 50 characters")
    .field("email")
    .required("Email is required")
    .email()
    .field("password")
    .required("Password is required")
    .password()
    .field("confirmPassword")
    .required("Please confirm your password")
    .field("department")
    .required("Department is required")
    .field("employeeId")
    .required("Employee ID is required")
    .employeeId(),

  profile: new ValidationSchema()
    .field("name")
    .required("Name is required")
    .minLength(2)
    .maxLength(50)
    .field("email")
    .required("Email is required")
    .email()
    .field("phone")
    .phone()
    .field("department")
    .required("Department is required")
    .field("employeeId")
    .required("Employee ID is required")
    .employeeId(),

  changePassword: new ValidationSchema()
    .field("currentPassword")
    .required("Current password is required")
    .field("newPassword")
    .required("New password is required")
    .password()
    .field("confirmPassword")
    .required("Please confirm your new password"),

  leaveRequest: new ValidationSchema()
    .field("startDate")
    .required("Start date is required")
    .date()
    .field("endDate")
    .required("End date is required")
    .date()
    .field("type")
    .required("Leave type is required")
    .field("reason")
    .required("Reason is required")
    .minLength(10, "Please provide a detailed reason (at least 10 characters)"),
};

// Form validation helper
export const validateForm = (data, schema) => {
  if (typeof schema === "string") {
    // Use pre-built schema
    const predefinedSchema = validationSchemas[schema];
    if (!predefinedSchema) {
      throw new Error(`Unknown validation schema: ${schema}`);
    }
    return predefinedSchema.validate(data);
  } else if (schema instanceof ValidationSchema) {
    // Use custom schema
    return schema.validate(data);
  } else {
    throw new Error("Invalid schema type");
  }
};

// Field-level validation for real-time feedback
export const validateField = (fieldName, value, schema) => {
  const tempData = { [fieldName]: value };
  const result = validateForm(tempData, schema);

  return {
    isValid: !result.errors[fieldName],
    error: result.errors[fieldName] || null,
  };
};

// Special validation functions
export const validatePasswordMatch = (password, confirmPassword) => {
  return validators.match(password, "Passwords do not match")(confirmPassword);
};

export const validateDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) {
    return { isValid: true, error: null };
  }

  const start = new Date(startDate);
  const end = new Date(endDate);

  if (end < start) {
    return { isValid: false, error: "End date must be after start date" };
  }

  return { isValid: true, error: null };
};

export const validateFileUpload = (
  file,
  maxSize = 5 * 1024 * 1024,
  allowedTypes = ["image/jpeg", "image/png", "image/jpg"]
) => {
  const errors = [];

  if (!file) {
    return { isValid: false, errors: ["Please select a file"] };
  }

  // Check file size
  if (file.size > maxSize) {
    errors.push(`File size must be less than ${maxSize / 1024 / 1024}MB`);
  }

  // Check file type
  if (!allowedTypes.includes(file.type)) {
    errors.push(`File type must be one of: ${allowedTypes.join(", ")}`);
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// Async validation (for server-side checks)
export const createAsyncValidator = (validationFn, errorMessage) => {
  return async (value) => {
    try {
      const isValid = await validationFn(value);
      return {
        isValid,
        error: isValid ? null : errorMessage,
      };
    } catch (error) {
      return {
        isValid: false,
        error: "Validation failed",
      };
    }
  };
};

// Email availability check (example async validator)
export const validateEmailAvailability = createAsyncValidator(async (email) => {
  // This would make an API call to check if email is available
  // For demo purposes, we'll simulate the check
  await new Promise((resolve) => setTimeout(resolve, 500));

  // Simulate some emails being taken
  const takenEmails = ["admin@test.com", "user@test.com"];
  return !takenEmails.includes(email.toLowerCase());
}, "This email is already registered");

// Employee ID availability check (example async validator)
export const validateEmployeeIdAvailability = createAsyncValidator(
  async (employeeId) => {
    await new Promise((resolve) => setTimeout(resolve, 300));

    const takenIds = ["EMP001", "EMP002", "ADMIN01"];
    return !takenIds.includes(employeeId.toUpperCase());
  },
  "This employee ID is already in use"
);

// Validation error formatter
export const formatValidationErrors = (errors) => {
  if (typeof errors === "string") {
    return errors;
  }

  if (Array.isArray(errors)) {
    return errors.join(", ");
  }

  if (typeof errors === "object") {
    return Object.values(errors).join(", ");
  }

  return "Validation failed";
};

// Form submission helper with validation
export const validateAndSubmit = async (data, schema, submitFn) => {
  try {
    // Validate the form
    const validation = validateForm(data, schema);

    if (!validation.isValid) {
      return {
        success: false,
        errors: validation.errors,
      };
    }

    // If validation passes, submit the form
    const result = await submitFn(data);

    return {
      success: true,
      data: result,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message || "Submission failed",
    };
  }
};

export default {
  validators,
  ValidationSchema,
  validationSchemas,
  validateForm,
  validateField,
  validatePasswordMatch,
  validateDateRange,
  validateFileUpload,
  createAsyncValidator,
  validateEmailAvailability,
  validateEmployeeIdAvailability,
  formatValidationErrors,
  validateAndSubmit,
};
