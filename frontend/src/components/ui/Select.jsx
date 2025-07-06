import React from 'react';
import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../utils/helpers';

const Select = React.forwardRef(({
  className,
  options = [],
  error = false,
  disabled = false,
  label,
  helper,
  placeholder = 'Select an option...',
  ...props
}, ref) => {
  const baseClasses = 'w-full px-3 py-2 border rounded-lg transition-all duration-200 bg-white focus:outline-none focus:ring-2 focus:ring-offset-0 appearance-none cursor-pointer';
  const normalClasses = 'border-gray-300 focus:ring-primary-500 focus:border-transparent';
  const errorClasses = 'border-red-500 focus:ring-red-500 focus:border-transparent';
  const disabledClasses = 'bg-gray-50 text-gray-500 cursor-not-allowed';

  const selectClasses = cn(
    baseClasses,
    error ? errorClasses : normalClasses,
    disabled && disabledClasses,
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
        <motion.select
          ref={ref}
          disabled={disabled}
          className={selectClasses}
          whileFocus={{ scale: 1.01 }}
          transition={{ duration: 0.1 }}
          {...props}
        >
          <option value="" disabled>
            {placeholder}
          </option>
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </motion.select>

        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <ChevronDown className="w-4 h-4 text-gray-400" />
        </div>
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

Select.displayName = 'Select';

export default Select;