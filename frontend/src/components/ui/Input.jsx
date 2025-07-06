import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/helpers';

const Input = React.forwardRef(({
  className,
  type = 'text',
  error = false,
  disabled = false,
  label,
  helper,
  icon,
  ...props
}, ref) => {
  const baseClasses = 'w-full px-3 py-2 border rounded-lg transition-all duration-200 placeholder-gray-400 bg-white focus:outline-none focus:ring-2 focus:ring-offset-0';
  const normalClasses = 'border-gray-300 focus:ring-primary-500 focus:border-transparent';
  const errorClasses = 'border-red-500 focus:ring-red-500 focus:border-transparent';
  const disabledClasses = 'bg-gray-50 text-gray-500 cursor-not-allowed';

  const inputClasses = cn(
    baseClasses,
    error ? errorClasses : normalClasses,
    disabled && disabledClasses,
    icon && 'pl-10',
    className
  );

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}

      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <div className="text-gray-400">
              {icon}
            </div>
          </div>
        )}

        <motion.input
          ref={ref}
          type={type}
          disabled={disabled}
          className={inputClasses}
          whileFocus={{ scale: 1.01 }}
          transition={{ duration: 0.1 }}
          {...props}
        />
      </div>

      {(helper || error) && (
        <motion.p
          className={cn(
            'mt-1 text-xs',
            error ? 'text-red-600' : 'text-gray-500'
          )}
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {error || helper}
        </motion.p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;