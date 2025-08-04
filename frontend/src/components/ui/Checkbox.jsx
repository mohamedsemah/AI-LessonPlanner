import React from 'react';

const Checkbox = ({ 
  checked, 
  onChange, 
  disabled = false, 
  readOnly = false,
  className = '',
  ...props 
}) => {
  return (
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      disabled={disabled}
      readOnly={readOnly}
      className={`w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2 ${
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
      } ${className}`}
      {...props}
    />
  );
};

export default Checkbox; 