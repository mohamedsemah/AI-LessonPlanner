import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/helpers';

const Badge = React.forwardRef(({
  className,
  variant = 'default',
  size = 'md',
  children,
  ...props
}, ref) => {
  const baseClasses = 'inline-flex items-center font-medium rounded-full border transition-colors';

  const variants = {
    default: 'bg-gray-100 text-gray-800 border-gray-200',
    primary: 'bg-primary-100 text-primary-800 border-primary-200',
    secondary: 'bg-secondary-100 text-secondary-800 border-secondary-200',
    success: 'bg-green-100 text-green-800 border-green-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    danger: 'bg-red-100 text-red-800 border-red-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200',
    remember: 'bg-red-100 text-red-800 border-red-200',
    understand: 'bg-orange-100 text-orange-800 border-orange-200',
    apply: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    analyze: 'bg-green-100 text-green-800 border-green-200',
    evaluate: 'bg-blue-100 text-blue-800 border-blue-200',
    create: 'bg-purple-100 text-purple-800 border-purple-200'
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  return (
    <motion.span
      ref={ref}
      className={cn(
        baseClasses,
        variants[variant],
        sizes[size],
        className
      )}
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.2 }}
      {...props}
    >
      {children}
    </motion.span>
  );
});

Badge.displayName = 'Badge';

export default Badge;