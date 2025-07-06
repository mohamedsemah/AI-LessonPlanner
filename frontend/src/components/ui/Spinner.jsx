import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/helpers';

const Spinner = React.forwardRef(({
  className,
  size = 'md',
  color = 'primary',
  ...props
}, ref) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colors = {
    primary: 'border-primary-600 border-t-transparent',
    secondary: 'border-gray-600 border-t-transparent',
    white: 'border-white border-t-transparent',
    current: 'border-current border-t-transparent'
  };

  return (
    <motion.div
      ref={ref}
      className={cn(
        'inline-block border-2 rounded-full animate-spin',
        sizes[size],
        colors[color],
        className
      )}
      initial={{ rotate: 0 }}
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      {...props}
    />
  );
});

Spinner.displayName = 'Spinner';

export default Spinner;