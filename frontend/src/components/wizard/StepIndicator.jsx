import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { cn, getStepStatus } from '../../utils/helpers';

const StepIndicator = ({ steps, currentStep }) => {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(currentStep, index);
          const isActive = status === 'active';
          const isCompleted = status === 'completed';
          const isInactive = status === 'inactive';

          return (
            <div key={step.id} className="flex items-center flex-1">
              {/* Step Circle */}
              <div className="relative flex items-center">
                <motion.div
                  className={cn(
                    'flex items-center justify-center w-10 h-10 rounded-full border-2 font-medium text-sm transition-all duration-300',
                    isActive && 'bg-primary-600 border-primary-600 text-white shadow-lg',
                    isCompleted && 'bg-green-600 border-green-600 text-white',
                    isInactive && 'bg-gray-100 border-gray-300 text-gray-500'
                  )}
                  initial={false}
                  animate={{
                    scale: isActive ? 1.1 : 1,
                    boxShadow: isActive ? '0 0 0 4px rgba(59, 130, 246, 0.15)' : '0 0 0 0px rgba(59, 130, 246, 0)'
                  }}
                  transition={{ duration: 0.2 }}
                >
                  {isCompleted ? (
                    <motion.div
                      initial={{ scale: 0, rotate: -90 }}
                      animate={{ scale: 1, rotate: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Check className="w-5 h-5" />
                    </motion.div>
                  ) : (
                    <span>{index + 1}</span>
                  )}
                </motion.div>

                {/* Step content - hidden on mobile */}
                <div className="hidden md:block ml-4 min-w-0 flex-1">
                  <div className={cn(
                    'text-sm font-medium transition-colors duration-300',
                    isActive && 'text-primary-600',
                    isCompleted && 'text-green-600',
                    isInactive && 'text-gray-500'
                  )}>
                    {step.title}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {step.description}
                  </div>
                </div>
              </div>

              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="flex-1 mx-4">
                  <div className="relative">
                    <div className="h-0.5 bg-gray-200 w-full" />
                    <motion.div
                      className="h-0.5 bg-primary-600 absolute top-0 left-0"
                      initial={{ width: '0%' }}
                      animate={{
                        width: index < currentStep ? '100%' : '0%'
                      }}
                      transition={{ duration: 0.5, delay: 0.1 }}
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Mobile step titles */}
      <div className="md:hidden mt-4 text-center">
        <div className="text-sm font-medium text-gray-900">
          {steps[currentStep]?.title}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Step {currentStep + 1} of {steps.length}
        </div>
      </div>
    </div>
  );
};

export default StepIndicator;